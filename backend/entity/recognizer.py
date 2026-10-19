from backend.retrieval.kg_retriever import kg_retriever


class MedicalEntityRecognizer:

    def __init__(self):
        self.refresh_entities()

    def refresh_entities(self):

        diseases = kg_retriever.get_all_diseases()

        self.diseases = [
            disease["disease"]
            for disease in diseases
        ]

    def recognize(self, text):

        text_lower = text.lower()

        entities = {
            "diseases": []
        }

        for disease in self.diseases:

            if disease.lower() in text_lower:

                entities["diseases"].append({
                    "name": disease,
                    "type": "Disease"
                })

        return entities


entity_recognizer = MedicalEntityRecognizer()