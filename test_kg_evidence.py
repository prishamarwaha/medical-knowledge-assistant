from backend.retrieval.kg_retriever import kg_retriever


disease = "Primary Hypertension"

evidence = kg_retriever.get_evidence_for_disease(
    disease
)

print("\n==============================")
print("KG EVIDENCE")
print("==============================")

for item in evidence:
    print(
        f"\n{item['evidence_id']}"
        f"\nSubject : {item['subject']}"
        f"\nRelation: {item['relation']}"
        f"\nObject  : {item['object']}"
    )