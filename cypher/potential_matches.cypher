# Should return potential matches based on similar interests of a particular user and number of interests in common with #a particular user
#Considerations:
#1. ensure that person is not already a match with returned persons (to be implemented)
#2. check to make sure that people returned have similar interests in common and ensure gender interests are considered. #For e.g. if Bob is interested in men, females or straight males would not be potential matches (implemented, currently #assuming Interested_in is a String value)


# VERSION 1
#===================================================================================================
MATCH (p:Person)-[:LOOKING_FOR]->(Picture)<-[:LOOKING_FOR]-(s:Person), (Picture)-[:RELATED_TO]->(Interest)  WHERE p.name='Bobby Boy' AND s.gender CONTAINS p.Interested_in AND s.Interested_in CONTAINS p.gender
RETURN s.name as potential_matches, count(Interest.name) as pics_in_common
ORDER BY pics_in_common DESC
#===================================================================================================




#VERSION 2
#Additions:
# ensure that the specified person is not already interested in returned persons and check for interests in common and ensure gender interests are considered 
# one way to add weight to the relationship is by simply calculating the percentage match based on the number of picture #interests in common other users have with the specified user 
#===================================================================================================
MATCH (me)-[:LOOKING_FOR]->(mee:Picture)
WHERE me.name='Monica beep'
WITH me,count(mee) as total_interests_to_compare
MATCH (me)-[:LOOKING_FOR]->(Picture)<-[:LOOKING_FOR]-(others:Person)
WHERE me.Interested_in CONTAINS others.gender 
AND others.Interested_in CONTAINS me.gender
AND NOT (me)-[:INTERESTED_IN]-(others)
AND NOT me=others
RETURN others.name as potential_matches, count(Picture.url) as num_pics_matched, total_interests_to_compare,
count(Picture.url)*100/total_interests_to_compare+'%' as percentage_match
#===================================================================================================