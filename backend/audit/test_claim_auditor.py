
from claim_auditor import build_claim_audit


def test_claim_audit():
    answer = (
        "Primary hypertension may be treated with ACE inhibitors. "
        "Regular exercise can help manage blood pressure."
    )

    kg_evidence = [
        {
            "evidence_id": "KG-001",
            "subject": "Primary Hypertension",
            "relation": "TREATED_WITH",
            "object": "ACE Inhibitor",
            "source": "Neo4j Medical Knowledge Graph",
        }
    ]

    literature_evidence = [
        {
            "id": "PUBMED-001",
            "title": "Treatment of Primary Hypertension",
            "text": (
                "ACE inhibitors are used in the treatment "
                "of primary hypertension."
            ),
            "source": "PubMed",
        }
    ]

    validation_result = {
        "overall_status": "PENDING",
        "rules": [
            {"rule": "R1", "status": "PASS"},
            {"rule": "R2", "status": "PENDING"},
        ],
    }

    result = build_claim_audit(
        answer=answer,
        kg_evidence=kg_evidence,
        literature_evidence=literature_evidence,
        validation_result=validation_result,
    )

    assert result["claim_count"] == 2
    assert result["overall_validation_status"] == "PENDING"
    assert result["claims"][0]["support_status"] == "PENDING_VALIDATION"

    assert result["claims"][1]["support_status"] == "NO_MATCHED_EVIDENCE"

    print(result)


if __name__ == "__main__":
    test_claim_audit()
