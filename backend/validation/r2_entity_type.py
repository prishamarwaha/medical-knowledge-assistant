class R2EntityType:

    VALID_ENTITY_TYPES = {
        "Disease",
        "Drug",
        "Symptom",
        "Test",
        "RiskFactor",
        "Complication"
    }

    def validate(self, entities):
        """
        R2: Validate the medical entity type.

        Full ontology validation against SNOMED CT / MeSH
        will be activated after UMLS integration.
        """

        if not entities:
            return {
                "rule": "R2",
                "status": "FAIL",
                "reason": "No entities available for validation."
            }

        diseases = entities.get("diseases", [])

        if not diseases:
            return {
                "rule": "R2",
                "status": "FAIL",
                "reason": "No medical entity type available."
            }

        invalid_types = []

        for entity in diseases:

            entity_type = entity.get("type")

            if entity_type not in self.VALID_ENTITY_TYPES:
                invalid_types.append(entity_type)

        if invalid_types:
            return {
                "rule": "R2",
                "status": "FAIL",
                "reason": (
                    f"Unsupported entity types: {invalid_types}"
                )
            }

        return {
            "rule": "R2",
            "status": "PENDING",
            "reason": (
                "Entity type is valid, but final ontology "
                "validation requires UMLS/SNOMED CT/MeSH."
            ),
            "entity_types": [
                entity.get("type")
                for entity in diseases
            ]
        }


r2_entity_type = R2EntityType()