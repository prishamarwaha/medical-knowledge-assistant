from backend.retrieval.reconciliation import reconciler


question = (
    "What are the treatments "
    "for primary hypertension?"
)


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
            "source": "PubMed",
            "pmid": "001"
        },
        "distance": 0.20
    }
]


result = reconciler.reconcile(
    question,
    kg_evidence,
    vector_evidence
)


print("\n==============================")
print("RECONCILIATION RESULT")
print("==============================")

print("\nStatus:")
print(result["status"])

print("\nIntent:")
print(result["intent"])

print("\nReason:")
print(result["reason"])

print("\nKG evidence count:")
print(result["kg_evidence_count"])

print("\nVector evidence count:")
print(result["vector_evidence_count"])

print("\nComparisons:")

for comparison in result["comparisons"]:

    print("\n-----------------------------")

    print(
        "KG Evidence:",
        comparison["kg_evidence_id"]
    )

    print(
        "Relation:",
        comparison["relation"]
    )

    print(
        "Object:",
        comparison["object"]
    )

    print(
        "Vector Evidence:",
        comparison["vector_evidence_id"]
    )

    print(
        "Overlap:",
        comparison["overlap"]
    )

    print(
        "Matching terms:",
        comparison["matching_terms"]
    )