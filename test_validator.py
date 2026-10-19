from backend.validation.evidence_validator import (
    evidence_validator
)

question = (
    "What are the treatments "
    "for primary hypertension?"
)

entities = {
    "diseases": [
        {
            "name": "Primary Hypertension",
            "type": "Disease"
        }
    ]
}

linked_entities = [
    {
        "original_entity": "Primary Hypertension",
        "linked_entity": "Primary Hypertension",
        "entity_type": "Disease",
        "status": "linked"
    }
]

kg_evidence = [
    {
        "evidence_id": "KG-001",
        "subject": "Primary Hypertension",
        "relation": "TREATED_WITH",
        "object": "ACE inhibitors",
        "source": "Neo4j Medical Knowledge Graph"
    }
]

vector_evidence = [
    {
        "id": "pubmed_001_chunk_0",
        "document": (
            "Primary hypertension is commonly managed "
            "with antihypertensive therapy. ACE inhibitors "
            "are among the medications used in treatment."
        ),
        "metadata": {
            "source": "PubMed"
        },
        "distance": 0.20
    }
]

reconciliation = {
    "status": "AGREEMENT",
    "supported_pairs": 1
}

result = evidence_validator.validate(
    question,
    entities,
    linked_entities,
    kg_evidence,
    vector_evidence,
    reconciliation
)

print("\n==============================")
print("R1-R5 VALIDATION")
print("==============================")

for rule, value in result["rules"].items():

    print(
        f"\n{rule}: {value['status']}"
    )

    print(
        "Reason:",
        value["reason"]
    )

print("\n------------------------------")
print("Overall:", result["status"])
print("Passed:", result["passed_rules"])
print("Failed:", result["failed_rules"])
print("Pending:", result["pending_rules"])