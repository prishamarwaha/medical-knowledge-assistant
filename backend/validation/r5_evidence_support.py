class R5EvidenceSupport:

    def validate(
        self,
        kg_evidence,
        vector_evidence,
        reconciliation
    ):
        """
        R5: Verify that retrieved evidence actually
        supports the query through reconciliation.
        """

        if not kg_evidence and not vector_evidence:
            return {
                "rule": "R5",
                "status": "FAIL",
                "reason": "No evidence was retrieved."
            }

        if not reconciliation:
            return {
                "rule": "R5",
                "status": "FAIL",
                "reason": "No reconciliation result available."
            }

        status = reconciliation.get(
            "status",
            "UNKNOWN"
        )

        supported_pairs = reconciliation.get(
            "supported_pairs",
            0
        )

        if status == "AGREEMENT" and supported_pairs > 0:
            return {
                "rule": "R5",
                "status": "PASS",
                "reason": (
                    "KG evidence has supporting literature "
                    "evidence identified during reconciliation."
                ),
                "supported_pairs": supported_pairs
            }

        if status == "CONFLICT":
            return {
                "rule": "R5",
                "status": "FAIL",
                "reason": (
                    "Retrieved evidence contains conflicting "
                    "support signals."
                ),
                "supported_pairs": supported_pairs
            }

        return {
            "rule": "R5",
            "status": "FAIL",
            "reason": (
                "Retrieved evidence does not provide "
                "sufficient cross-source support."
            ),
            "supported_pairs": supported_pairs
        }


r5_evidence_support = R5EvidenceSupport()