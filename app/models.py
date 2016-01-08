from django.db import models
from django.contrib.auth.models import User

from neomodel import (
    StructuredNode,
    DateProperty, IntegerProperty, StringProperty, ArrayProperty,
    Relationship, RelationshipTo, RelationshipFrom, StructuredRel,
    db,
)


class UserProfile(models.Model):
    MALE = 'M'
    FEMALE = 'F'

    INTERESTED_IN_MEN = 1
    INTERESTED_IN_WOMEN = 2
    INTERESTED_IN_BOTH = 3

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
    interested_in = models.IntegerField(choices=INTERESTED_IN)
    description = models.CharField(max_length=300, null=True, blank=True)
    profilePicture = models.URLField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            super(UserProfile, self).save(*args, **kwargs)
            user_node = Person.from_database_profile(self)
            user_node.save()
        else:
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
    weight = IntegerProperty(default=1)


class Person(StructuredNode):
    user_profile_id = IntegerProperty(unique_index=True, required=True)
    name = StringProperty()
    gender = StringProperty(required=True, choices=UserProfile.GENDER)
    interested_in = ArrayProperty(required=True)  # men, women, or both
    date_of_birth = DateProperty(required=True)

    looking_for = RelationshipTo('Picture', 'LOOKING_FOR')
    interested_in_rel = RelationshipTo('Person', 'INTERESTED_IN')
    recommanded = Relationship('Person', 'RECOMMANDED', model=RecommandedRel)

    # in the database, interested_in is a number (1 = men, 2 = women, 3 = both)
    # in the graph, it is an array (e.g. [1, 2] = both men and women)
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

        user_profile_id = profile.user.pk
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
        user = Person.nodes.filter(user_profile_id=profile.user.pk)[0][0]
        user.name = profile.user.username
        user.gender = profile.gender
        user.interested_in = Person.interested_in_array(profile.interested_in)
        user.date_of_birth = profile.dob
        user.save()

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
