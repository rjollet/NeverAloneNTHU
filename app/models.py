from django.db import models
from django.contrib.auth.models import User

from neomodel import (
    StructuredNode,
    DateProperty, IntegerProperty, StringProperty, ArrayProperty,
    Relationship, RelationshipTo, RelationshipFrom, StructuredRel,
    db, ZeroOrOne,
)


class UserProfile(models.Model):
    MALE = 'M'
    FEMALE = 'F'

    INTERESTED_IN_MEN = 'M'
    INTERESTED_IN_WOMEN = 'F'
    INTERESTED_IN_BOTH = 'B'

    GENDER = (
        (MALE, 'Man'),
        (FEMALE, 'Woman'),
    )

    INTERESTED_IN = (
        (INTERESTED_IN_MEN, 'Men'),
        (INTERESTED_IN_WOMEN, 'Women'),
        (INTERESTED_IN_BOTH, 'Both'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dob = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER)
    interested_in = models.CharField(max_length=1, choices=INTERESTED_IN)
    description = models.CharField(max_length=500, null=True, blank=True)
    profilePicture = models.URLField(max_length=500, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            super(UserProfile, self).save(*args, **kwargs)
            user_node = Person.from_database_profile(self)
            user_node.save()
        else:
            super(UserProfile, self).save(*args, **kwargs)
            Person.update_persone_profile(self)


class Interest(StructuredNode):
    label = StringProperty(unique_index=True, required=True)

    # RelationshipFrom/To enforces the direction of edges:
    # a picture is RELATED_TO a interest, not the other way around
    pictures = RelationshipFrom('Picture', 'RELATED_TO')


class Picture(StructuredNode):
    pictureURL = StringProperty(unique_index=True, required=True)

    tags = RelationshipTo('Interest', 'RELATED_TO')
    persons_looking_for = RelationshipFrom('Person', 'LOOKING_FOR')


class RecommandedRel(StructuredRel):
    weight = IntegerProperty(default=0)

class Person(StructuredNode):
    user_profile_id = IntegerProperty(unique_index=True, required=True)
    name = StringProperty()
    gender = StringProperty(required=True, choices=UserProfile.GENDER)
    interested_in = ArrayProperty(required=True)  # men, women, or both
    date_of_birth = DateProperty(required=True)

    looking_for = RelationshipTo('Picture', 'LOOKING_FOR')
    interested_in_rel = RelationshipTo('Person', 'INTERESTED_IN')
    recommanded = Relationship('Person', 'RECOMMANDED', model=RecommandedRel)

    # in the database, interested_in is a number (M = men, F = women, B = both)
    # in the graph, it is an array (e.g. [M, F] = both men and women)
    def interested_in_array(interested_in):
        if interested_in == UserProfile.INTERESTED_IN_BOTH:
            return [
                UserProfile.INTERESTED_IN_MEN,
                UserProfile.INTERESTED_IN_WOMEN]
        return [interested_in]

    @classmethod
    def from_database_profile(cls, profile):
        """
        Create a Person node object from the UserProfile database object (not automatically saved).

        parameters
        ----------
        profile: UserProfile

        returns
        -------
        Person
        """
        name = profile.user.username

        user_profile_id = profile.pk
        gender = profile.gender

        interested_in = cls.interested_in_array(profile.interested_in)

        date_of_birth = profile.dob

        return Person(
            user_profile_id=user_profile_id,
            name=name,
            gender=gender,
            interested_in=interested_in,
            date_of_birth=date_of_birth,
        )

    @db.transaction
    def update_persone_profile(profile):
        user = Person.nodes.filter(user_profile_id=profile.pk)[0][0]
        user.name = profile.user.username
        user.gender = profile.gender
        user.interested_in = Person.interested_in_array(profile.interested_in)
        user.date_of_birth = profile.dob
        user.save()


    #http://neomodel.readthedocs.org/en/latest/cypher.html
    def interested_in_me(self):
        """
        Return people interested in me
        """
        results, columns = self.cypher("START me=node({self}) MATCH others-[:INTERESTED_IN]->me WHERE NOT (me)-[:INTERESTED_IN]->(others) RETURN others.user_profile_id")
        return [UserProfile.objects.get(pk=row[0]) for row in results]

    def matches(self):
        """
        We are interested in each other
        """
        results, columns = self.cypher("START me=node({self}) MATCH (others)-[:INTERESTED_IN]->(me)-[:INTERESTED_IN]->(others) RETURN others.user_profile_id")
        return [UserProfile.objects.get(pk=row[0]) for row in results]

     #not yet tested
    def potential_matches(self, limit=10):
        """
        Find potential matches based on picture interests
        We used differents queries using differents colaborative filtering
        - resultsLookingFor: use the similarity based on the common picture both user are looking for
        - resultsInterestedIn: use the smilarity based on if you are interested in the same people
        """

        def combine_item_pairs(l1, l2):
            D = {k:v for (k, v) in l1}
            for (key, value) in l2:
                if key in D:
                    D[key] = (D[key] + value)/2
                else:
                    D[key] = value
            return [(key, D[key]) for key in D]

        resultsRandom, columns = self.cypher("""
            START me=node({self})
            MATCH (others:Person)
            WHERE others.gender in me.interested_in
            AND me.gender in others.interested_in
            AND NOT (me)-[:INTERESTED_IN]->(others)
            AND NOT me=others
            RETURN others.user_profile_id, 0
            SKIP (toInt(RAND()*100)%3)+1 LIMIT 10""")

        resultsRecommanded, columns = self.cypher("""
            START me=node({self})
            MATCH (me:Person)-[rel:RECOMMANDED]-(others:Person)
            WHERE others.gender in me.interested_in
            AND me.gender in others.interested_in
            AND NOT (me)-[:INTERESTED_IN]->(others)
            AND NOT me=others
            AND rel.weight>0
            WITH me, others, toFloat(rel.weight) as val
            MATCH (me:Person)-[allRel:RECOMMANDED]-(:Person)
            WHERE allRel.weight>0
            RETURN others.user_profile_id, val/sum(allRel.weight) as sim
            LIMIT 10""")

        resultsLookingFor, columns = self.cypher("""
            START me=node({self})
            MATCH (me)-[:LOOKING_FOR]-(picture:Picture)-[:LOOKING_FOR]-(others)
            WHERE others.gender in me.interested_in
            AND me.gender in others.interested_in
            AND NOT (me)-[:INTERESTED_IN]->(others)
            AND NOT me=others
            WITH me,others,toFloat(count(picture)) as intersection
            MATCH (me)-[:LOOKING_FOR]-(pme:Picture)
            , (others)-[:LOOKING_FOR]-(pothers:Picture)
            RETURN others.user_profile_id, intersection/(count(pme)+count(pothers)-intersection) AS sim_jaccard
            ORDER BY sim_jaccard DESC
            LIMIT 100""")

        resultsRElatedTo, columns = self.cypher("""
            START me=node({self})
            MATCH (me)-[:LOOKING_FOR]-(:Picture)-[:RELATED_TO]-(i:Interest)-[rel:RELATED_TO]-(:Picture)-[:LOOKING_FOR]-(others)
            WHERE others.gender in me.interested_in
            AND me.gender in others.interested_in
            AND NOT (me)-[:INTERESTED_IN]->(others)
            AND NOT me=others
            WITH me,others,toFloat(count(i)) as intersection
            MATCH (me)-[:LOOKING_FOR]-(:Picture)-[:RELATED_TO]-(ime:Interest)
            , (others)-[:LOOKING_FOR]-(:Picture)-[:RELATED_TO]-(iothers:Interest)
            RETURN others.user_profile_id, intersection/(count(ime)+count(iothers)-intersection) AS sim_jaccard
            ORDER BY sim_jaccard DESC
            LIMIT 100
            """)
        print(resultsRElatedTo)

        resultsInterestedIn, columns = self.cypher("""
            START me=node({self})
            MATCH (me)-[:INTERESTED_IN]->(sameInterest:Person)<-[:INTERESTED_IN]-(similarme)
            WHERE NOT me=similarme
            WITH similarme,me,toFloat(count(sameInterest)) as intersection
            MATCH (me)-[:INTERESTED_IN]->(meInterest:Person)
                , (similarme)-[:INTERESTED_IN]->(others:Person)
            WHERE others.gender in me.interested_in
            AND me.gender in others.interested_in
            AND NOT (me)-[:INTERESTED_IN]->(others)
            AND NOT me=others
            RETURN others.user_profile_id, intersection/(count(meInterest)+count(others)-intersection) AS sim_jaccard
            ORDER BY sim_jaccard DESC
            LIMIT 100""")

        results1 = combine_item_pairs([(row[0],row[1]) for row in resultsRecommanded], [(row[0],row[1]) for row in resultsRandom])
        results2 = combine_item_pairs([(row[0],row[1]) for row in resultsLookingFor], [(row[0],row[1]) for row in resultsRElatedTo])
        results3 = combine_item_pairs([(row[0],row[1]) for row in resultsInterestedIn], results1)
        results = combine_item_pairs(results2, results3)
        results.sort(key=lambda tup: tup[1])
        results.reverse()
        print(results)
        return [UserProfile.objects.get(pk=row[0]) for row in results[0:limit]]


    def get_random_not_looking_for_pictures(self, limit=10):
        """
        Return a random list of Picture-s that the Person is not yet LOOKING_FOR.
        """
        results, columns = self.cypher(
            "START person=node({self}) "
            "MATCH (p:Picture) "  # get all the pictures
            "WHERE NOT (p)<-[:LOOKING_FOR]-(person) "  # that the Person is not LOOKING_FOR
            "WITH p, RAND() as r RETURN p ORDER BY r LIMIT {limit}",  # randomly selecting {limit} of them
            params={'limit': limit})

        pictures = [Picture.inflate(row[0]) for row in results]
        return pictures

    def get_random_couple(self):
        """
        Return a random couple of two people may look good together
        """
        results, columns = self.cypher("""
            MATCH
                  (p1:Person)
                , (p2:Person)
            WHERE
                NOT (p1)-[:INTERESTED_IN]-(p2)
            AND NOT p1=p2
            AND p1.gender in p2.interested_in
            AND p2.gender in p1.interested_in
            RETURN p1.user_profile_id, p2.user_profile_id
            SKIP toInt(RAND()*10000) LIMIT 1
            """)
        couples = [(UserProfile.objects.get(pk=row[0]), UserProfile.objects.get(pk=row[1])) for row in results]
        return couples[0]
