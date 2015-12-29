# Find all the people the logged in user has shown interest in
MATCH (me)-[:INTERESTED_IN]->(others) WHERE me.name='Bobby Boy' return others.name as MyInterests


# Find all the people that has shown interest in the logged in user
MATCH (others)-[:INTERESTED_IN]->(me) WHERE me.name='Luke Foop' return others.name as PeopleInterestedInMe


# Find all the people that you have expressed interest in and they with you

MATCH (others)-[:INTERESTED_IN]->(me)-[:INTERESTED_IN]->(others) WHERE me.name='Bobby Boy' return others.name as InterestedInEachOther
