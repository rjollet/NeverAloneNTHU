# will return potential matches based on similar interests of a particular user, number of matches 

Considerations:
1. ensure that person is not already a match wth returned persons (to be implemented)
2. check to make sure that people returned have similar interests and ensure gender interests are considered. For e.g. if Bob is gay, females or straight males should not be returned (implemented, currently assuming Interested_in is a String value)



MATCH (p:Person)-[:LOOKING_FOR]->(Picture)<-[:LOOKING_FOR]-(s:Person), (Picture)-[:RELATED_TO]->(Interest)  WHERE p.name='Bobby Boy' AND s.gender CONTAINS p.Interested_in AND s.Interested_in CONTAINS p.gender
RETURN s.name as potential_matches, count(Interest.name) as pics_in_common
ORDER BY pics_in_common DESC
