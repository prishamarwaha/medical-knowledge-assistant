import re


class RetrievalReconciler:

    def extract_terms_from_text(
        self,
        text
    ):

        if not text:
            return set()

        text = str(text).lower()

        words = re.findall(
            r"\b[a-zA-Z]{4,}\b",
            text
        )

        stop_words = {

            "this",
            "that",
            "with",
            "from",
            "have",
            "will",
            "into",
            "also",
            "their",
            "there",
            "which",
            "about",
            "would",
            "should",
            "could",
            "through",
            "where",
            "when",
            "what",

            "medical",
            "disease",
            "information",

            "include",
            "includes",
            "including",

            "used",
            "using",

            "common",
            "commonly",

            "focuses",
            "focus",

            "based",

            "result",
            "results"

        }

        terms = set()

        for word in words:

            if word in stop_words:
                continue

            word = self.normalize_term(
                word
            )

            if len(word) >= 4:

                terms.add(
                    word
                )

        return terms


    # ==========================================
    # NORMALIZE TERMS
    # ==========================================

    def normalize_term(
        self,
        word
    ):

        word = word.lower()

        # Simple plural normalization

        if (
            word.endswith("ies")
            and len(word) > 5
        ):

            word = (
                word[:-3]
                +
                "y"
            )

        elif (
            word.endswith("s")
            and not word.endswith("ss")
            and len(word) > 4
        ):

            word = word[:-1]

        return word


    # ==========================================
    # EXTRACT KG TERMS
    # ==========================================

    def extract_kg_terms(
        self,
        kg_context
    ):

        terms = set()

        if not kg_context:
            return terms

        for item in kg_context:

            if isinstance(
                item,
                dict
            ):

                for key, value in item.items():

                    # Extract terms from KG field names

                    terms.update(
                        self.extract_terms_from_text(
                            key
                        )
                    )


                    # Extract terms from values

                    if isinstance(
                        value,
                        list
                    ):

                        for entry in value:

                            terms.update(
                                self.extract_terms_from_text(
                                    entry
                                )
                            )

                    else:

                        terms.update(
                            self.extract_terms_from_text(
                                value
                            )
                        )

            else:

                terms.update(
                    self.extract_terms_from_text(
                        item
                    )
                )

        return terms


    # ==========================================
    # EXTRACT VECTOR TERMS
    # ==========================================

    def extract_vector_terms(
        self,
        vector_results
    ):

        terms = set()

        if not vector_results:
            return terms

        for result in vector_results:

            if isinstance(
                result,
                dict
            ):

                document = result.get(
                    "document",
                    ""
                )

                terms.update(
                    self.extract_terms_from_text(
                        document
                    )
                )

            else:

                terms.update(
                    self.extract_terms_from_text(
                        result
                    )
                )

        return terms


    # ==========================================
    # RECONCILIATION
    # ==========================================

    def reconcile(
        self,
        kg_context,
        vector_results
    ):

        kg_terms = (
            self.extract_kg_terms(
                kg_context
            )
        )


        vector_terms = (
            self.extract_vector_terms(
                vector_results
            )
        )


        matching_terms = sorted(
            list(
                kg_terms.intersection(
                    vector_terms
                )
            )
        )


        kg_term_count = len(
            kg_terms
        )


        vector_term_count = len(
            vector_terms
        )


        matching_term_count = len(
            matching_terms
        )


        # ==========================================
        # HANDLE NO EVIDENCE
        # ==========================================

        if (
            kg_term_count == 0
            and
            vector_term_count == 0
        ):

            status = (
                "INSUFFICIENT_EVIDENCE"
            )

            confidence = 0.0


        elif kg_term_count == 0:

            status = (
                "KG_NO_RESULTS"
            )

            confidence = 0.0


        elif vector_term_count == 0:

            status = (
                "VECTOR_NO_RESULTS"
            )

            confidence = 0.0


        # ==========================================
        # CALCULATE AGREEMENT
        # ==========================================

        else:

            # Use smaller evidence set as reference.
            #
            # This is better than Jaccard because
            # KG and Vector DB naturally contain
            # different amounts of information.

            smaller_set_size = min(

                kg_term_count,

                vector_term_count

            )


            confidence = (

                matching_term_count

                /

                smaller_set_size

            )


            # Prevent values above 1

            confidence = min(
                confidence,
                1.0
            )


            # ======================================
            # STATUS
            # ======================================

            if confidence >= 0.40:

                status = (
                    "AGREEMENT"
                )


            elif confidence >= 0.20:

                status = (
                    "PARTIAL_AGREEMENT"
                )


            else:

                status = (
                    "NO_AGREEMENT"
                )


        return {

            "status":
                status,


            "confidence":
                round(
                    confidence,
                    2
                ),


            "kg_term_count":
                kg_term_count,


            "vector_term_count":
                vector_term_count,


            "matching_term_count":
                matching_term_count,


            "matching_terms":
                matching_terms

        }


reconciler = (
    RetrievalReconciler()
)