class EvidenceGate:

    def evaluate(self, validation_result):

        if not validation_result:
            return {
                "status": "REJECTED",
                "allow_generation": False,
                "reason": "No validation result available."
            }

        rules = validation_result.get(
            "rules",
            {}
        )

        failed_rules = [
            rule
            for rule, result in rules.items()
            if result.get("status") == "FAIL"
        ]

        pending_rules = [
            rule
            for rule, result in rules.items()
            if result.get("status") == "PENDING"
        ]

        if failed_rules:
            return {
                "status": "REJECTED",
                "allow_generation": False,
                "failed_rules": failed_rules,
                "pending_rules": pending_rules,
                "reason": (
                    "One or more evidence validation "
                    "rules failed."
                )
            }

        if pending_rules:
            return {
                "status": "PENDING",
                "allow_generation": False,
                "failed_rules": failed_rules,
                "pending_rules": pending_rules,
                "reason": (
                    "Evidence cannot be admitted until "
                    "all required validation rules pass."
                )
            }

        return {
            "status": "VERIFIED",
            "allow_generation": True,
            "failed_rules": [],
            "pending_rules": [],
            "reason": (
                "All evidence validation rules passed."
            )
        }


evidence_gate = EvidenceGate()