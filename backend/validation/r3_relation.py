class R3RelationValidator:

    VALID_RELATIONS = {
        "HAS_SYMPTOM",
        "DIAGNOSED_BY",
        "TREATED_WITH",
        "HAS_RISK_FACTOR",
        "HAS_COMPLICATION",
        "SUPPORTED_BY",
    }

    def validate(self, kg_evidence):
        """
        R3: Validate KG relations against the approved
        relation set.
        """

        if not kg_evidence:
            return {
                "rule": "R3",
                "status": "FAIL",
                "reason": "No KG relationships were retrieved.",
            }

        invalid = []

        for evidence in kg_evidence:
            relation = evidence.get("relation")

            if relation not in self.VALID_RELATIONS:
                invalid.append(relation)

        if invalid:
            return {
                "rule": "R3",
                "status": "FAIL",
                "reason": f"Unsupported KG relations: {invalid}",
            }

        return {
            "rule": "R3",
            "status": "PASS",
            "reason": (
                "All KG relationships belong to the approved "
                "relation set."
            ),
            "validated_relations": [
                evidence.get("relation")
                for evidence in kg_evidence
            ],
        }


r3_relation = R3RelationValidator()