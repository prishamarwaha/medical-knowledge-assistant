from neo4j import GraphDatabase
from backend.config import (
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD,
    NEO4J_DATABASE
)


class Neo4jDatabase:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        self.database = NEO4J_DATABASE

    def verify_connection(self):
        with self.driver.session(database=self.database) as session:
            result = session.run(
                "RETURN 'Neo4j Medical Knowledge Graph Connected' AS message"
            )
            return result.single()["message"]

    def close(self):
        self.driver.close()


db = Neo4jDatabase()