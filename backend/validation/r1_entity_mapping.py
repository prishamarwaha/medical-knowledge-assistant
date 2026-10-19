class R1EntityMapping:

    def validate(self, entities, linked_entities):
        """
        R1: Verify that recognized medical entities
        are successfully mapped to a KG entity.
        """

        if not entities:
            return {
                "rule": "R1",
                "status": "FAIL",
                "reason": "No entities were recognized."
            }

        recognized = entities.get("diseases", [])

        if not recognized:
            return {
                "rule": "R1",
                "status": "FAIL",
                "reason": "No medical disease entity was recognized."
            }

        if not linked_entities:
            return {
                "rule": "R1",
                "status": "FAIL",
                "reason": "Recognized entities were not linked."
            }

        linked = [
            item
            for item in linked_entities
            if item.get("status") == "linked"
        ]

        if len(linked) < len(recognized):
            return {
                "rule": "R1",
                "status": "FAIL",
                "reason": (
                    "One or more recognized entities "
                    "could not be linked to the knowledge graph."
                )
            }

        return {
            "rule": "R1",
            "status": "PASS",
            "reason": (
                "All recognized disease entities were "
                "successfully mapped."
            ),
            "mapped_entities": linked
        }


r1_entity_mapping = R1EntityMapping()