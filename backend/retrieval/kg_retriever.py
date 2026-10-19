from backend.database import db


class KnowledgeGraphRetriever:

    def __init__(self):
        self.db = db

    def run_query(self, query, parameters=None):
        parameters = parameters or {}

        with self.db.driver.session(
            database=self.db.database
        ) as session:

            result = session.run(query, parameters)

            return [
                record.data()
                for record in result
            ]

    # ------------------------------------------------
    # GET COMPLETE DISEASE INFORMATION
    # ------------------------------------------------

    def get_disease_info(self, disease_name):

        query = """
        MATCH (d:Disease)
        WHERE toLower(d.name) = toLower($disease_name)

        OPTIONAL MATCH (d)-[:HAS_SYMPTOM]->(s:Symptom)
        OPTIONAL MATCH (d)-[:DIAGNOSED_BY]->(t:Test)
        OPTIONAL MATCH (d)-[:TREATED_WITH]->(dr:Drug)
        OPTIONAL MATCH (d)-[:HAS_RISK_FACTOR]->(rf:RiskFactor)
        OPTIONAL MATCH (d)-[:HAS_COMPLICATION]->(c:Complication)

        RETURN
            d.name AS disease,

            collect(DISTINCT s.name) AS symptoms,

            collect(DISTINCT t.name) AS tests,

            collect(DISTINCT dr.name) AS drugs,

            collect(DISTINCT rf.name) AS risk_factors,

            collect(DISTINCT c.name) AS complications
        """

        results = self.run_query(
            query,
            {
                "disease_name": disease_name
            }
        )

        return results

    # ------------------------------------------------
    # GET DISEASE BY SYMPTOM
    # ------------------------------------------------

    def get_diseases_by_symptom(self, symptom_name):

        query = """
        MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom)

        WHERE toLower(s.name) = toLower($symptom_name)

        RETURN
            d.name AS disease,
            s.name AS symptom
        """

        return self.run_query(
            query,
            {
                "symptom_name": symptom_name
            }
        )

    # ------------------------------------------------
    # GET DRUGS FOR DISEASE
    # ------------------------------------------------

    def get_drugs_for_disease(self, disease_name):

        query = """
        MATCH (d:Disease)-[:TREATED_WITH]->(dr:Drug)

        WHERE toLower(d.name) = toLower($disease_name)

        RETURN
            d.name AS disease,
            collect(DISTINCT dr.name) AS drugs
        """

        return self.run_query(
            query,
            {
                "disease_name": disease_name
            }
        )

    # ------------------------------------------------
    # GET TESTS FOR DISEASE
    # ------------------------------------------------

    def get_tests_for_disease(self, disease_name):

        query = """
        MATCH (d:Disease)-[:DIAGNOSED_BY]->(t:Test)

        WHERE toLower(d.name) = toLower($disease_name)

        RETURN
            d.name AS disease,
            collect(DISTINCT t.name) AS tests
        """

        return self.run_query(
            query,
            {
                "disease_name": disease_name
            }
        )

    # ------------------------------------------------
    # GET ALL DISEASES
    # ------------------------------------------------

    def get_all_diseases(self):

        query = """
        MATCH (d:Disease)

        RETURN
            d.name AS disease

        ORDER BY disease
        """

        return self.run_query(query)
    def get_evidence_for_disease(self, disease_name):
        """
        Retrieve explicit KG triples for a disease.
        Each relationship is returned as an auditable evidence item.
        """

        query = """
        MATCH (d:Disease)
        WHERE toLower(d.name) = toLower($disease_name)

        OPTIONAL MATCH (d)-[r]->(target)

        RETURN
            d.name AS subject,
            type(r) AS relation,
            target.name AS object
        """

        records = self.run_query(
            query,
            {"disease_name": disease_name}
        )

        evidence = []

        for index, record in enumerate(records):

            if not record["relation"]:
                continue

            evidence.append({
                "evidence_id": f"KG-{index + 1:03d}",
                "subject": record["subject"],
                "relation": record["relation"],
                "object": record["object"],
                "source": "Neo4j Medical Knowledge Graph"
            })

        return evidence
        


kg_retriever = KnowledgeGraphRetriever()