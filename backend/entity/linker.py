from backend.retrieval.kg_retriever import kg_retriever


class MedicalEntityLinker:

    def link_entity(self, entity):

        entity_name = entity["name"]
        entity_type = entity["type"]

        if entity_type == "Disease":

            diseases = kg_retriever.get_all_diseases()

            for disease in diseases:

                if disease["disease"].lower() == entity_name.lower():

                    return {
                        "original_entity": entity_name,
                        "linked_entity": disease["disease"],
                        "entity_type": "Disease",
                        "status": "linked"
                    }

        return {
            "original_entity": entity_name,
            "linked_entity": None,
            "entity_type": entity_type,
            "status": "not_linked"
        }


entity_linker = MedicalEntityLinker()