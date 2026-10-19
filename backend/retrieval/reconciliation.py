import re


class RetrievalReconciler:
    """
    Query-aware reconciliation between Neo4j KG evidence
    and PubMed/vector evidence.

    Possible outcomes:
        AGREEMENT
        CONFLICT
        INSUFFICIENT_SUPPORT
    """

    INTENT_KEYWORDS = {
        "treatment": [
            "treatment",
            "treat",
            "therapy",
            "therapies",
            "management",
            "medication",
            "drug",
            "drugs"
        ],
        "symptoms": [
            "symptom",
            "symptoms",
            "sign",
            "signs",
            "manifestation",
            "clinical features"
        ],
        "diagnosis": [
            "diagnosis",
            "diagnostic",
            "diagnose",
            "test",
            "testing",
            "screening"
        ],
        "risk_factors": [
            "risk",
            "risk factor",
            "risk factors",
            "cause",
            "causes",
            "etiology"
        ],
        "complications": [
            "complication",
            "complications",
            "effect",
            "effects",
            "consequence",
            "consequences"
        ]
    }

    RELATION_INTENTS = {
        "treatment": {
            "TREATED_WITH"
        },
        "symptoms": {
            "HAS_SYMPTOM"
        },
        "diagnosis": {
            "DIAGNOSED_BY"
        },
        "risk_factors": {
            "HAS_RISK_FACTOR"
        },
        "complications": {
            "HAS_COMPLICATION"
        }
    }

    def detect_intent(self, question):
        question_lower = question.lower()

        detected = []

        for intent, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in question_lower:
                    detected.append(intent)
                    break

        if detected:
            return detected[0]

        return "general"

    def normalize(self, text):
        if not text:
            return ""

        text = str(text).lower()

        text = re.sub(
            r"[^a-z0-9\s-]",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    def tokenize(self, text):
        normalized = self.normalize(text)

        if not normalized:
            return set()

        return set(
            word
            for word in normalized.split()
            if len(word) >= 3
        )

    def calculate_term_overlap(self, text_a, text_b):
        tokens_a = self.tokenize(text_a)
        tokens_b = self.tokenize(text_b)

        if not tokens_a or not tokens_b:
            return 0.0, set()

        common = tokens_a.intersection(tokens_b)

        denominator = min(
            len(tokens_a),
            len(tokens_b)
        )

        if denominator == 0:
            return 0.0, set()

        return (
            len(common) / denominator,
            common
        )

    def get_relevant_kg_evidence(
        self,
        kg_evidence,
        intent
    ):
        """
        Keep KG relationships relevant to the
        user's question intent.
        """

        if not kg_evidence:
            return []

        valid_relations = self.RELATION_INTENTS.get(
            intent,
            set()
        )

        if not valid_relations:
            return kg_evidence

        relevant = [
            evidence
            for evidence in kg_evidence
            if evidence.get("relation") in valid_relations
        ]

        return relevant

    def build_kg_text(self, evidence):
        return " ".join([
            str(evidence.get("subject", "")),
            str(evidence.get("relation", "")),
            str(evidence.get("object", ""))
        ])

    def build_vector_text(self, evidence):
        return str(
            evidence.get("document", "")
        )

    def compare_evidence(
        self,
        question,
        kg_evidence,
        vector_evidence
    ):
        """
        Compare KG and literature evidence using:
        - question intent
        - KG relation
        - subject/object terms
        - literature text overlap
        """

        intent = self.detect_intent(question)

        relevant_kg = self.get_relevant_kg_evidence(
            kg_evidence,
            intent
        )

        if not relevant_kg:
            return {
                "status": "INSUFFICIENT_SUPPORT",
                "reason": (
                    "No KG relationship directly supports "
                    "the detected question intent."
                ),
                "intent": intent,
                "comparisons": []
            }

        if not vector_evidence:
            return {
                "status": "INSUFFICIENT_SUPPORT",
                "reason": (
                    "No literature evidence was retrieved "
                    "for comparison."
                ),
                "intent": intent,
                "comparisons": []
            }

        comparisons = []

        for kg_item in relevant_kg:

            subject = kg_item.get(
                "subject",
                ""
            )

            relation = kg_item.get(
                "relation",
                ""
            )

            object_name = kg_item.get(
                "object",
                ""
            )

            kg_text = self.build_kg_text(
                kg_item
            )

            best_overlap = 0.0
            best_vector = None
            best_terms = set()

            for vector_item in vector_evidence:

                vector_text = self.build_vector_text(
                    vector_item
                )

                overlap, matching_terms = (
                    self.calculate_term_overlap(
                        kg_text,
                        vector_text
                    )
                )

                if overlap > best_overlap:
                    best_overlap = overlap
                    best_vector = vector_item
                    best_terms = matching_terms

            comparisons.append({
                "kg_evidence_id": kg_item.get(
                    "evidence_id"
                ),
                "subject": subject,
                "relation": relation,
                "object": object_name,
                "vector_evidence_id": (
                    best_vector.get("id")
                    if best_vector
                    else None
                ),
                "overlap": round(
                    best_overlap,
                    3
                ),
                "matching_terms": sorted(
                    best_terms
                )
            })

        supported = [
            item
            for item in comparisons
            if item["overlap"] >= 0.20
        ]

        if supported:
            return {
                "status": "AGREEMENT",
                "reason": (
                    "KG evidence relevant to the question "
                    "has supporting literature evidence."
                ),
                "intent": intent,
                "comparisons": comparisons,
                "supported_pairs": len(supported)
            }

        return {
            "status": "INSUFFICIENT_SUPPORT",
            "reason": (
                "KG evidence was retrieved, but the "
                "literature evidence does not provide "
                "sufficient support for the KG relationships."
            ),
            "intent": intent,
            "comparisons": comparisons,
            "supported_pairs": 0
        }

    def reconcile(
        self,
        question,
        kg_evidence,
        vector_evidence
    ):
        """
        Main reconciliation entry point.
        """

        result = self.compare_evidence(
            question,
            kg_evidence,
            vector_evidence
        )

        return {
            "status": result["status"],
            "intent": result["intent"],
            "reason": result["reason"],
            "comparisons": result["comparisons"],
            "supported_pairs": result.get(
                "supported_pairs",
                0
            ),
            "kg_evidence_count": len(
                kg_evidence or []
            ),
            "vector_evidence_count": len(
                vector_evidence or []
            )
        }


reconciler = RetrievalReconciler()