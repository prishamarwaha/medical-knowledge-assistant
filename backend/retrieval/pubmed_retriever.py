import os
import requests
import chromadb

from sentence_transformers import SentenceTransformer


class PubMedRetriever:

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

    def __init__(self):
        self.email = os.getenv("NCBI_EMAIL")
        self.api_key = os.getenv("NCBI_API_KEY")

        self.client = chromadb.PersistentClient(
            path="data/vector_db"
        )

        self.embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        self.collection = self.client.get_or_create_collection(
            name="pubmed_medical"
        )

    def _request_params(self, extra_params):
        params = {
            "tool": "MedicalRAG",
            "email": self.email,
            **extra_params
        }

        if self.api_key:
            params["api_key"] = self.api_key

        return params

    def search_pubmed(self, query, max_results=10):

        params = self._request_params({
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": max_results
        })

        response = requests.get(
            self.BASE_URL + "esearch.fcgi",
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        return data["esearchresult"]["idlist"]

    def fetch_articles(self, pmids):

        if not pmids:
            return []

        params = self._request_params({
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
            "rettype": "abstract"
        })

        response = requests.get(
            self.BASE_URL + "efetch.fcgi",
            params=params,
            timeout=60
        )

        response.raise_for_status()

        return self._parse_articles(response.text)

    def _parse_articles(self, xml_text):

        import xml.etree.ElementTree as ET

        root = ET.fromstring(xml_text)

        articles = []

        for article in root.findall(".//PubmedArticle"):

            pmid_element = article.find(".//PMID")
            title_element = article.find(".//ArticleTitle")

            if pmid_element is None:
                continue

            pmid = pmid_element.text or ""

            title = ""
            if title_element is not None:
                title = "".join(
                    title_element.itertext()
                )

            abstract_parts = []

            for abstract_text in article.findall(
                ".//Abstract/AbstractText"
            ):
                text = "".join(
                    abstract_text.itertext()
                )

                if text:
                    abstract_parts.append(text)

            abstract = " ".join(abstract_parts)

            if not abstract:
                continue

            articles.append({
                "pmid": pmid,
                "title": title,
                "abstract": abstract
            })

        return articles

    def chunk_text(self, text, chunk_size=800, overlap=150):
        """
        Split medical text into overlapping chunks.
        Keeps enough context while making retrieval more precise.
        """

        words = text.split()

        chunks = []

        start = 0

        while start < len(words):
            end = start + chunk_size

            chunk = " ".join(words[start:end])

            if chunk.strip():
                chunks.append(chunk)

            if end >= len(words):
                break

            start = end - overlap

        return chunks


    def ingest_articles(self, articles):

        if not articles:
            return 0

        documents = []
        ids = []
        metadatas = []

        for article in articles:

            full_text = (
                f"Title: {article['title']}\n\n"
                f"Abstract: {article['abstract']}"
            )

            chunks = self.chunk_text(full_text)

            for chunk_index, chunk in enumerate(chunks):

                document_id = (
                    f"pubmed_{article['pmid']}_chunk_{chunk_index}"
                )

                documents.append(chunk)

                ids.append(document_id)

                metadatas.append({
                    "source": "PubMed",
                    "pmid": article["pmid"],
                    "title": article["title"],
                    "chunk_index": chunk_index
                })

        embeddings = self.embedding_model.encode(
            documents,
            show_progress_bar=True
        ).tolist()

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

        return len(documents)

    def search_vector(self, query, top_k=5):

        query_embedding = (
            self.embedding_model
            .encode([query])
            .tolist()
        )

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

        output = []

        if not results.get("ids"):
            return output

        for i in range(len(results["ids"][0])):

            output.append({
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })

        return output
    def build_pubmed_query(self, question, entities=None):
        """
        Construct a more focused PubMed query from the
        user's question and detected medical entities.
        """

        question_lower = question.lower()

        # Use recognized diseases when available
        disease_terms = []

        if entities:
            for disease in entities.get("diseases", []):
                if isinstance(disease, dict):
                    name = disease.get("name")
                else:
                    name = disease

                if name:
                    disease_terms.append(
                        f'"{name}"'
                    )

        # Fallback if no entity was detected
        if not disease_terms:
            disease_terms = [question.strip()]

        disease_query = " OR ".join(disease_terms)

        # Detect broad clinical intent
        if any(
            word in question_lower
            for word in [
                "treatment",
                "treat",
                "therapy",
                "management",
                "drug",
                "medication"
            ]
        ):
            intent_query = (
                "treatment OR therapy OR management "
                "OR therapeutic OR medication"
            )

        elif any(
            word in question_lower
            for word in [
                "symptom",
                "symptoms",
                "sign",
                "clinical"
            ]
        ):
            intent_query = (
                "symptom OR symptoms OR "
                "clinical manifestation"
            )

        elif any(
            word in question_lower
            for word in [
                "diagnosis",
                "diagnostic",
                "diagnose",
                "test"
            ]
        ):
            intent_query = (
                "diagnosis OR diagnostic OR test"
            )

        elif any(
            word in question_lower
            for word in [
                "cause",
                "causes",
                "risk",
                "risk factor"
            ]
        ):
            intent_query = (
                "cause OR etiology OR "
                "risk factor"
            )

        elif any(
            word in question_lower
            for word in [
                "complication",
                "complications"
            ]
        ):
            intent_query = (
                "complication OR complications"
            )

        else:
            intent_query = ""

        if intent_query:
            return (
                f"({disease_query}) AND "
                f"({intent_query})"
            )

        return disease_query
    def search_pubmed_for_question(
    self,
    question,
    entities=None,
    max_results=10
):
        """
        Query-aware PubMed retrieval.
        """

        query = self.build_pubmed_query(
            question,
            entities
        )

        print("\nPubMed query:")
        print(query)

        pmids = self.search_pubmed(
            query,
            max_results=max_results
        )

        articles = self.fetch_articles(pmids)

        return {
            "query": query,
            "pmids": pmids,
            "articles": articles
        }


pubmed_retriever = PubMedRetriever()