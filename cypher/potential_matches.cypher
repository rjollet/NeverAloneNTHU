# Should return potential matches based on similar interests of a particular user and number of interests in common with a particular user

Considerations:
1. ensure that person is not already a match wth returned persons (to be implemented)
2. check to make sure that people returned have similar interests in common and ensure gender interests are considered. For e.g. if Bob is interested in men, females or straight males would not be potential matches (implemented, currently assuming Interested_in is a String value)


MATCH (p:Person)-[:LOOKING_FOR]->(Picture)<-[:LOOKING_FOR]-(s:Person), (Picture)-[:RELATED_TO]->(Interest)  WHERE p.name='Bobby Boy' AND s.gender CONTAINS p.Interested_in AND s.Interested_in CONTAINS p.gender
RETURN s.name as potential_matches, count(Interest.name) as pics_in_common
ORDER BY pics_in_common DESC
