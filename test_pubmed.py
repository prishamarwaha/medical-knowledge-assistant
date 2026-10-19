from backend.retrieval.pubmed_retriever import pubmed_retriever


question = "What are the treatments for primary hypertension?"

entities = {
    "diseases": [
        {
            "name": "Primary Hypertension",
            "type": "Disease"
        }
    ]
}


result = pubmed_retriever.search_pubmed_for_question(
    question,
    entities,
    max_results=10
)


print("\n================================")
print("GENERATED PUBMED QUERY")
print("================================")

print(result["query"])


print("\n================================")
print("PMIDS")
print("================================")

print(result["pmids"])


print("\n================================")
print("ARTICLES")
print("================================")

for article in result["articles"][:3]:

    print("\n-----------------------------")
    print("PMID:", article["pmid"])
    print("TITLE:", article["title"])
    print("ABSTRACT:")
    print(article["abstract"][:500])