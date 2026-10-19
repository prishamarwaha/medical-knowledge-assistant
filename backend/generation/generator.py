class MedicalResponseGenerator:

    def generate(
        self,
        question,
        kg_context,
        vector_results,
        reconciliation
    ):

        question_lower = question.lower()

        # ----------------------------------------
        # DEFAULT VALUES
        # ----------------------------------------

        disease = None

        symptoms = []

        tests = []

        drugs = []

        risk_factors = []

        complications = []


        # ----------------------------------------
        # EXTRACT KG INFORMATION
        # ----------------------------------------

        if kg_context:

            for item in kg_context:

                if not isinstance(
                    item,
                    dict
                ):
                    continue


                # DISEASE

                if not disease:

                    disease = (

                        item.get("Disease")

                        or item.get("disease")

                        or item.get("name")
                    )


                # SYMPTOMS

                item_symptoms = (

                    item.get("Symptoms")

                    or item.get("symptoms")

                    or []
                )

                if item_symptoms:

                    symptoms.extend(
                        item_symptoms
                    )


                # TESTS

                item_tests = (

                    item.get("Tests")

                    or item.get("tests")

                    or []
                )

                if item_tests:

                    tests.extend(
                        item_tests
                    )


                # DRUGS

                item_drugs = (

                    item.get("Drugs")

                    or item.get("drugs")

                    or []
                )

                if item_drugs:

                    drugs.extend(
                        item_drugs
                    )


                # RISK FACTORS

                item_risk_factors = (

                    item.get("RiskFactors")

                    or item.get("risk_factors")

                    or []
                )

                if item_risk_factors:

                    risk_factors.extend(
                        item_risk_factors
                    )


                # COMPLICATIONS

                item_complications = (

                    item.get("Complications")

                    or item.get("complications")

                    or []
                )

                if item_complications:

                    complications.extend(
                        item_complications
                    )


        # ----------------------------------------
        # REMOVE DUPLICATES
        # ----------------------------------------

        symptoms = list(
            dict.fromkeys(symptoms)
        )

        tests = list(
            dict.fromkeys(tests)
        )

        drugs = list(
            dict.fromkeys(drugs)
        )

        risk_factors = list(
            dict.fromkeys(risk_factors)
        )

        complications = list(
            dict.fromkeys(complications)
        )


        # ----------------------------------------
        # GENERATE DIRECT ANSWER
        # ----------------------------------------

        direct_answer = ""


        # TREATMENT QUESTION

        if (

            "treatment" in question_lower

            or "treat" in question_lower

            or "medicine" in question_lower

            or "drug" in question_lower

        ):

            if drugs:

                disease_name = disease or "this condition"

                direct_answer = (

                    f"For {disease_name}, treatment "
                    f"focuses on managing the condition "
                    f"and its underlying cause. "

                    f"Treatment options in the Knowledge "
                    f"Graph include: "

                    f"{', '.join(drugs)}."
                )


        # SYMPTOM QUESTION

        elif (

            "symptom" in question_lower

            or "sign" in question_lower

        ):

            if symptoms:

                disease_name = disease or "this condition"

                direct_answer = (

                    f"Common symptoms associated with "
                    f"{disease_name} include: "

                    f"{', '.join(symptoms)}."
                )


        # DIAGNOSIS QUESTION

        elif (

            "diagnos" in question_lower

            or "test" in question_lower

        ):

            if tests:

                disease_name = disease or "this condition"

                direct_answer = (

                    f"Diagnostic evaluation for "
                    f"{disease_name} may include: "

                    f"{', '.join(tests)}."
                )


        # RISK FACTOR QUESTION

        elif (

            "risk" in question_lower

            or "cause" in question_lower

        ):

            if risk_factors:

                disease_name = disease or "this condition"

                direct_answer = (

                    f"Risk factors associated with "
                    f"{disease_name} include: "

                    f"{', '.join(risk_factors)}."
                )


        # COMPLICATION QUESTION

        elif (

            "complication" in question_lower

            or "effect" in question_lower

        ):

            if complications:

                disease_name = disease or "this condition"

                direct_answer = (

                    f"Possible complications of "
                    f"{disease_name} include: "

                    f"{', '.join(complications)}."
                )


        # GENERAL QUESTION

        else:

            if disease:

                direct_answer = (

                    f"{disease} information was retrieved "
                    f"from the Medical Knowledge Graph."
                )


        # ----------------------------------------
        # FALLBACK ANSWER
        # ----------------------------------------

        if not direct_answer:

            direct_answer = (

                "I could not generate a direct answer "
                "from the current medical knowledge base."
            )


        # ----------------------------------------
        # BUILD ADDITIONAL INFORMATION
        # ----------------------------------------

        additional_information = []


        if symptoms:

            additional_information.append({

                "title": "Associated Symptoms",

                "content":

                    ", ".join(symptoms)
            })


        if tests:

            additional_information.append({

                "title": "Diagnostic Tests",

                "content":

                    ", ".join(tests)
            })


        if drugs:

            additional_information.append({

                "title": "Treatment Options",

                "content":

                    ", ".join(drugs)
            })


        if risk_factors:

            additional_information.append({

                "title": "Risk Factors",

                "content":

                    ", ".join(risk_factors)
            })


        if complications:

            additional_information.append({

                "title": "Possible Complications",

                "content":

                    ", ".join(complications)
            })


        # ----------------------------------------
        # VECTOR SUPPORTING INFORMATION
        # ----------------------------------------

        vector_information = ""


        if vector_results:

            top_result = vector_results[0]

            vector_information = (

                top_result.get(
                    "document",
                    ""
                )
                .strip()
                .replace("\n", " ")
            )


        # ----------------------------------------
        # RECONCILIATION
        # ----------------------------------------

        reconciliation_status = (

            reconciliation.get(
                "status",
                "UNKNOWN"
            )
        )


        confidence = (

            reconciliation.get(
                "confidence",
                0.0
            )
        )


        # ----------------------------------------
        # RETURN FINAL RESPONSE
        # ----------------------------------------

        return {

            # DIRECT ANSWER

            "answer":

                direct_answer,


            # KG ADDITIONAL INFORMATION

            "additional_information":

                additional_information,


            # VECTOR SUPPORTING TEXT

            "semantic_support":

                vector_information,


            # RECONCILIATION

            "reconciliation_status":

                reconciliation_status,


            "confidence":

                confidence,


            # SOURCES

            "sources": [

                "Neo4j Medical Knowledge Graph",

                "ChromaDB Vector Database"
            ]
        }


medical_response_generator = (
    MedicalResponseGenerator()
)