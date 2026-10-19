import re


class R4ContradictionValidator:
    """
    R4: Detect candidate contradictions between KG facts
    and literature evidence.

    This is a rule-based screening heuristic. It does not
    establish semantic contradiction or clinical truth.
    """

    TREATMENT_CONTRADICTION_SIGNALS = {
        "contraindicated",
        "contraindication",
        "not recommended",
        "should be avoided",
        "avoid use of",
        "ineffective",
        "does not improve",
        "did not improve",
        "no benefit",
        "not effective",
    }

    RISK_FACTOR_CONTRADICTION_SIGNALS = {
        "not associated with",
        "no association with",
        "not a risk factor",
        "was not associated with",
        "were not associated with",
        "did not increase the risk",
    }

    GENERAL_NEGATION_SIGNALS = {
        "not caused by",
        "not diagnosed by",
        "does not cause",
        "did not cause",
        "not a symptom of",
        "not a complication of",
    }

    def split_sentences(self, text):
        """Split text into approximate sentences."""
        if not text:
            return []

        return [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+", text)
            if sentence.strip()
        ]

    def get_signals(self, relation):
        if relation == "TREATED_WITH":
            return self.TREATMENT_CONTRADICTION_SIGNALS

        if relation == "HAS_RISK_FACTOR":
            return self.RISK_FACTOR_CONTRADICTION_SIGNALS

        return self.GENERAL_NEGATION_SIGNALS

    def validate(self, kg_evidence, vector_evidence):
        if not kg_evidence or not vector_evidence:
            return {
                "rule": "R4",
                "status": "PENDING",
                "reason": (
                    "Both KG and literature evidence are required "
                    "for contradiction analysis."
                ),
                "contradictions": [],
            }

        contradictions = []

        for kg_item in kg_evidence:
            object_name = str(
                kg_item.get("object", "")
            ).strip()

            relation = str(
                kg_item.get("relation", "")
            ).strip()

            if not object_name:
                continue

            signals = self.get_signals(relation)
            object_lower = object_name.lower()

            for vector_item in vector_evidence:
                document = str(
                    vector_item.get("document", "")
                )

                for sentence in self.split_sentences(document):
                    sentence_lower = sentence.lower()

                    # The object and signal must occur in the
                    # same sentence to become a candidate.
                    if object_lower not in sentence_lower:
                        continue

                    matched_signals = [
                        signal
                        for signal in signals
                        if signal in sentence_lower
                    ]

                    if not matched_signals:
                        continue

                    contradictions.append({
                        "kg_evidence_id": kg_item.get(
                            "evidence_id"
                        ),
                        "vector_evidence_id": vector_item.get(
                            "id"
                        ),
                        "subject": kg_item.get("subject"),
                        "relation": relation,
                        "object": object_name,
                        "reason": (
                            "A possible relation-specific "
                            "contradiction signal occurs in the "
                            "same sentence as the KG object. "
                            "Manual or semantic verification is "
                            "required."
                        ),
                        "matched_signals": matched_signals,
                        "evidence_sentence": sentence,
                    })

        if contradictions:
            return {
                "rule": "R4",
                "status": "FAIL",
                "reason": (
                    "Candidate contradiction signals were "
                    "detected and require verification."
                ),
                "contradictions": contradictions,
            }

        return {
            "rule": "R4",
            "status": "PASS",
            "reason": (
                "No configured relation-specific contradiction "
                "signals were detected in sentences mentioning "
                "the KG objects. This does not prove that no "
                "contradiction exists."
            ),
            "contradictions": [],
        }


r4_contradiction = R4ContradictionValidator()