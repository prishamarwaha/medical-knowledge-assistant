from backend.validation.r1_entity_mapping import (
    r1_entity_mapping
)

from backend.validation.r2_entity_type import (
    r2_entity_type
)

from backend.validation.r3_relation import (
    r3_relation
)

from backend.validation.r4_contradiction import (
    r4_contradiction
)

from backend.validation.r5_evidence_support import (
    r5_evidence_support
)


class EvidenceValidator:

    def validate(
        self,
        question,
        entities,
        linked_entities,
        kg_evidence,
        vector_evidence,
        reconciliation
    ):
        """
        Execute R1-R5 independently and return
        a unified validation result.
        """

        r1 = r1_entity_mapping.validate(
            entities,
            linked_entities
        )

        r2 = r2_entity_type.validate(
            entities
        )

        r3 = r3_relation.validate(
            kg_evidence
        )

        r4 = r4_contradiction.validate(
            kg_evidence,
            vector_evidence
        )

        r5 = r5_evidence_support.validate(
            kg_evidence,
            vector_evidence,
            reconciliation
        )

        rules = {
            "R1": r1,
            "R2": r2,
            "R3": r3,
            "R4": r4,
            "R5": r5
        }

        passed = sum(
            1
            for result in rules.values()
            if result["status"] == "PASS"
        )

        failed = sum(
            1
            for result in rules.values()
            if result["status"] == "FAIL"
        )

        pending = sum(
            1
            for result in rules.values()
            if result["status"] == "PENDING"
        )

        if failed > 0:
            overall_status = "REJECTED"

        elif pending > 0:
            overall_status = "PENDING"

        else:
            overall_status = "VERIFIED"

        return {
            "rules": rules,
            "passed_rules": passed,
            "failed_rules": failed,
            "pending_rules": pending,
            "total_rules": len(rules),
            "status": overall_status
        }


evidence_validator = EvidenceValidator()