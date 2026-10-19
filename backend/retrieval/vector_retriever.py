import chromadb

from sentence_transformers import (
    SentenceTransformer
)


class VectorRetriever:

    def __init__(self):

        # Persistent local Vector Database

        self.client = (
            chromadb.PersistentClient(
                path="data/vector_db"
            )
        )


        # Embedding model

        self.embedding_model = (
            SentenceTransformer(
                "all-MiniLM-L6-v2"
            )
        )


        # Load collection

        self.collection = (
            self.client.get_or_create_collection(
                name="medical_knowledge"
            )
        )


        # Initialize medical documents

        self.initialize_data()


    # ==========================================
    # INITIALIZE MEDICAL DOCUMENTS
    # ==========================================

    def initialize_data(self):

        documents = [


            """
            Type 1 Diabetes Mellitus is an autoimmune disease in
            which the body produces little or no insulin.

            Common symptoms include frequent urination,
            excessive thirst and unexplained weight loss.

            Diagnosis may involve HbA1c and blood glucose tests.

            Insulin therapy is commonly used for treatment.
            """,


            """
            Type 2 Diabetes Mellitus is characterized by insulin
            resistance and elevated blood glucose levels.

            Common symptoms include frequent urination,
            excessive thirst, fatigue and blurred vision.

            Diagnosis may involve HbA1c and fasting blood glucose.

            Treatment may include lifestyle management
            and medication.
            """,


            """
            Gestational Diabetes Mellitus develops during pregnancy
            and causes elevated blood glucose levels.

            Screening commonly involves glucose tolerance testing.

            Management may include diet, exercise and
            blood glucose monitoring.
            """,


            """
            Primary Hypertension is high blood pressure without an
            identifiable secondary medical cause.

            Risk factors include obesity, high sodium intake,
            physical inactivity and family history.

            Blood pressure measurement is used for diagnosis.

            Treatment may include lifestyle modification and
            antihypertensive medication.
            """,


            """
            Secondary Hypertension is high blood pressure caused by
            an underlying medical condition or medication.

            Diagnosis involves blood pressure measurement and
            investigation of the underlying cause.

            Treatment focuses on identifying and managing the
            underlying cause of hypertension.

            Antihypertensive medications may also be used to
            control blood pressure.
            """

        ]


        ids = [

            "type1_diabetes_v2",

            "type2_diabetes_v2",

            "gestational_diabetes_v2",

            "primary_hypertension_v2",

            "secondary_hypertension_v2"

        ]


        # ==========================================
        # CLEAR OLD DATA
        # ==========================================

        existing_ids = (
            self.collection.get()["ids"]
        )


        if existing_ids:

            self.collection.delete(
                ids=existing_ids
            )

            print(
                "Old Vector Database documents removed"
            )


        # ==========================================
        # CREATE EMBEDDINGS
        # ==========================================

        embeddings = (
            self.embedding_model.encode(
                documents
            )
            .tolist()
        )


        # ==========================================
        # ADD DOCUMENTS
        # ==========================================

        self.collection.add(

            documents=
                documents,


            embeddings=
                embeddings,


            ids=
                ids

        )


        print(
            "Updated medical documents added "
            "to Vector Database"
        )


    # ==========================================
    # VECTOR SEARCH
    # ==========================================

    def search(

        self,

        query,

        top_k=1,

        max_distance=1.0

    ):


        # Create query embedding

        query_embedding = (

            self.embedding_model.encode(
                [query]
            )

            .tolist()

        )


        # Search Vector Database

        results = (
            self.collection.query(

                query_embeddings=
                    query_embedding,


                n_results=1

            )
        )


        formatted_results = []


        # ==========================================
        # NO RESULTS
        # ==========================================

        if not results.get(
            "documents"
        ):

            return (
                formatted_results
            )


        if not results["documents"][0]:

            return (
                formatted_results
            )


        # ==========================================
        # FORMAT RESULTS
        # ==========================================

        for i in range(

            len(
                results["documents"][0]
            )

        ):


            distance = (

                results["distances"][0][i]

            )


            # ======================================
            # RELEVANCE FILTER
            # ======================================

            if (
                distance
                >
                max_distance
            ):

                continue


            formatted_results.append({

                "id":

                    results["ids"][0][i],


                "document":

                    results["documents"][0][i],


                "distance":

                    round(
                        distance,
                        4
                    )

            })


        return (
            formatted_results
        )


vector_retriever = (
    VectorRetriever()
)