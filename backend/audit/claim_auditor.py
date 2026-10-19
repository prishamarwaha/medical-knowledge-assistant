
import re
from typing import Any


STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been",
    "being", "to", "of", "in", "on", "for", "with", "and", "or",
    "that", "this", "it", "as", "by", "from", "can", "may", "does",
    "do", "have", "has", "had", "which", "what", "how"
}


def tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9-]+", (text or "").lower())
    return {
        word for word in words
        if word not in STOPWORDS and len(word) > 1
    }


def split_claims(answer: str) -> list[str]:
    if not answer or not answer.strip():
        return []

    parts = re.split(r"(?<=[.!?])\s+|\n+", answer.strip())
    return [part.strip() for part in parts if part.strip()]


def evidence_text(item: dict[str, Any]) -> str:
    fields = [
        "subject", "relation", "object",
        "text", "content", "document", "snippet", "title", "abstract"
    ]

    values = [str(item[key]) for key in fields if item.get(key)]

    metadata = item.get("metadata", {})
    if isinstance(metadata, dict):
        values.extend(
            str(metadata[key])
            for key in ("title", "abstract", "source", "pmid")
            if metadata.get(key)
        )

    return " ".join(values)


def match_score(claim: str, evidence: str) -> float:
    """Lexical overlap is a candidate-retrieval signal, not truth confidence."""
    claim_terms = tokenize(claim)
    evidence_terms = tokenize(evidence)

    if not claim_terms or not evidence_terms:
        return 0.0

    return round(
        len(claim_terms & evidence_terms) / len(claim_terms), 3
    )


def build_claim_audit(
    answer: str,
    kg_evidence: list[dict],
    literature_evidence: list[dict],
    validation_result: dict,
    min_overlap: float = 0.20,
) -> dict:
    overall_status = validation_result.get(
        "overall_status",
        validation_result.get("status", "PENDING")
)

    rules = validation_result.get(
        "rules",
        validation_result.get("results", [])
    )

    audited_claims = []

    for index, claim in enumerate(split_claims(answer), start=1):
        candidates = []

        for item in kg_evidence or []:
            score = match_score(claim, evidence_text(item))

            if score >= min_overlap:
                candidates.append({
                    "evidence_id": item.get(
                        "evidence_id", item.get("id")
                    ),
                    "source_type": "knowledge_graph",
                    "source": item.get(
                        "source", "Neo4j Medical Knowledge Graph"
                    ),
                    "subject": item.get("subject"),
                    "relation": item.get("relation"),
                    "object": item.get("object"),
                    "match_score": score,
                })

        for item in literature_evidence or []:
            score = match_score(claim, evidence_text(item))
            metadata = item.get("metadata", {})
            metadata = metadata if isinstance(metadata, dict) else {}

            if score >= min_overlap:
                candidates.append({
                    "evidence_id": (
                        item.get("evidence_id")
                        or item.get("id")
                        or metadata.get("pmid")
                    ),
                    "source_type": "literature",
                    "source": item.get("source", "PubMed / ChromaDB"),
                    "title": item.get("title") or metadata.get("title"),
                    "pmid": item.get("pmid") or metadata.get("pmid"),
                    "url": item.get("url") or metadata.get("url"),
                    "match_score": score,
                })

        candidates.sort(
            key=lambda item: item["match_score"],
            reverse=True
        )

        if not candidates:
            support_status = "NO_MATCHED_EVIDENCE"
        elif overall_status != "VERIFIED":
            support_status = "PENDING_VALIDATION"
        else:
            # Evidence matching alone cannot establish entailment.
            support_status = "CANDIDATE_SUPPORT_FOUND"

        audited_claims.append({
            "claim_id": f"CLM-{index:03d}",
            "claim": claim,
            "candidate_evidence": candidates,
            "support_status": support_status,
            "ontology_validation": overall_status,
            "validation_rules": rules,
        })

    return {
        "audit_version": "0.2",
        "overall_validation_status": overall_status,
        "claim_count": len(audited_claims),
        "claims": audited_claims,
        "limitations": [
            "Claims are split at sentence level; atomic claim decomposition is future work.",
            "Lexical overlap identifies candidate evidence, not clinical entailment.",
            "Candidate support is not proof that a claim is true.",
            "Ontology validation requires actual ontology integration.",
        ],
    }
