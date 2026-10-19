from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.audit.claim_auditor import build_claim_audit


# ==================================================
# DATABASE
# ==================================================

from backend.database import db


# ==================================================
# VALIDATION
# ==================================================

from backend.validation.evidence_validator import (
    evidence_validator
)

from backend.validation.gate import (
    evidence_gate
)


# ==================================================
# RETRIEVAL
# ==================================================

from backend.retrieval.kg_retriever import (
    kg_retriever
)

from backend.retrieval.pubmed_retriever import (
    pubmed_retriever
)

from backend.retrieval.vector_retriever import (
    vector_retriever
)

from backend.retrieval.reconciliation import (
    reconciler
)


# ==================================================
# ENTITY
# ==================================================

from backend.entity.recognizer import (
    entity_recognizer
)

from backend.entity.linker import (
    entity_linker
)


# ==================================================
# GENERATION
# ==================================================

from backend.generation.generator import (
    medical_response_generator
)


# ==================================================
# FASTAPI APPLICATION
# ==================================================

app = FastAPI(
    title="Medical Knowledge Graph RAG API",
    version="1.0.0"
)


# ==================================================
# CORS
# ==================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# ==================================================
# REQUEST MODEL
# ==================================================

class QuestionRequest(BaseModel):

    question: str


# ==================================================
# HOME
# ==================================================

@app.get("/")
def home():

    return {
        "message": "Medical RAG Backend is running"
    }


# ==================================================
# HEALTH CHECK
# ==================================================

@app.get("/health")
def health_check():

    try:

        message = db.verify_connection()

        return {
            "status": "healthy",
            "neo4j": "connected",
            "message": message
        }

    except Exception as e:

        return {
            "status": "unhealthy",
            "neo4j": "disconnected",
            "error": str(e)
        }


# ==================================================
# GET DISEASE
# ==================================================

@app.get("/disease/{disease_name}")
def get_disease(
    disease_name: str
):

    try:

        result = (
            kg_retriever.get_disease_info(
                disease_name
            )
        )

        return {
            "status": "success",
            "data": result
        }

    except Exception as e:

        return {
            "status": "error",
            "error": str(e)
        }


# ==================================================
# ENTITY RECOGNITION
# ==================================================

@app.post("/recognize")
def recognize_question(
    question: str
):

    try:

        entities = (
            entity_recognizer.recognize(
                question
            )
        )

        return {
            "status": "success",
            "question": question,
            "entities": entities
        }

    except Exception as e:

        return {
            "status": "error",
            "error": str(e)
        }


# ==================================================
# ENTITY LINKING
# ==================================================

@app.post("/link")
def link_question(
    question: str
):

    try:

        entities = (
            entity_recognizer.recognize(
                question
            )
        )

        linked_entities = []

        for entity in entities.get(
            "diseases",
            []
        ):

            linked_entity = (
                entity_linker.link_entity(
                    entity
                )
            )

            linked_entities.append(
                linked_entity
            )

        return {
            "status": "success",
            "question": question,
            "recognized_entities": entities,
            "linked_entities": linked_entities
        }

    except Exception as e:

        return {
            "status": "error",
            "error": str(e)
        }


# ==================================================
# KNOWLEDGE GRAPH SEARCH
# ==================================================

@app.post("/ask-kg")
def ask_knowledge_graph(
    question: str
):

    try:

        # ------------------------------------------
        # STEP 1
        # ENTITY RECOGNITION
        # ------------------------------------------

        entities = (
            entity_recognizer.recognize(
                question
            )
        )

        # ------------------------------------------
        # STEP 2
        # ENTITY LINKING
        # ------------------------------------------

        linked_entities = []

        for entity in entities.get(
            "diseases",
            []
        ):

            linked_entity = (
                entity_linker.link_entity(
                    entity
                )
            )

            linked_entities.append(
                linked_entity
            )

        # ------------------------------------------
        # STEP 3
        # KNOWLEDGE GRAPH RETRIEVAL
        # ------------------------------------------

        retrieved_context = []

        for entity in linked_entities:

            if entity.get(
                "status"
            ) != "linked":

                continue

            disease_name = entity.get(
                "linked_entity"
            )

            if not disease_name:
                continue

            disease_info = (
                kg_retriever.get_disease_info(
                    disease_name
                )
            )

            if disease_info:

                if isinstance(
                    disease_info,
                    list
                ):

                    retrieved_context.extend(
                        disease_info
                    )

                else:

                    retrieved_context.append(
                        disease_info
                    )

        # ------------------------------------------
        # RESPONSE
        # ------------------------------------------

        return {

            "status": "success",

            "question": question,

            "recognized_entities": entities,

            "linked_entities": linked_entities,

            "knowledge_graph_context":
                retrieved_context

        }

    except Exception as e:

        return {
            "status": "error",
            "error": str(e)
        }


# ==================================================
# VECTOR SEARCH
# ==================================================

@app.post("/search-vector")
def search_vector(
    question: str
):

    try:

        results = (
            vector_retriever.search(
                question
            )
        )

        return {

            "status": "success",

            "question": question,

            "retrieval_type":
                "semantic_vector_search",

            "results": results

        }

    except Exception as e:

        return {

            "status": "error",

            "error": str(e)

        }


# ==================================================
# HYBRID SEARCH
# ==================================================

@app.post("/hybrid-search")
def hybrid_search(
    question: str
):

    try:

        # ------------------------------------------
        # STEP 1
        # ENTITY RECOGNITION
        # ------------------------------------------

        entities = (
            entity_recognizer.recognize(
                question
            )
        )

        # ------------------------------------------
        # STEP 2
        # ENTITY LINKING
        # ------------------------------------------

        linked_entities = []

        for entity in entities.get(
            "diseases",
            []
        ):

            linked_entity = (
                entity_linker.link_entity(
                    entity
                )
            )

            linked_entities.append(
                linked_entity
            )

        # ------------------------------------------
        # STEP 3
        # KNOWLEDGE GRAPH
        # ------------------------------------------

        kg_context = []

        for entity in linked_entities:

            if entity.get(
                "status"
            ) != "linked":

                continue

            disease_name = entity.get(
                "linked_entity"
            )

            if not disease_name:
                continue

            results = (
                kg_retriever.get_disease_info(
                    disease_name
                )
            )

            if results:

                if isinstance(
                    results,
                    list
                ):

                    kg_context.extend(
                        results
                    )

                else:

                    kg_context.append(
                        results
                    )

        # ------------------------------------------
        # STEP 4
        # PUBMED VECTOR RETRIEVAL
        # ------------------------------------------

        pubmed_result = (
            pubmed_retriever.search_pubmed_for_question(
                question,
                entities,
                max_results=10
            )
        )

        pubmed_articles = (
            pubmed_result.get(
                "articles",
                []
            )
        )

        if pubmed_articles:

            pubmed_retriever.ingest_articles(
                pubmed_articles
            )

        vector_results = (
            pubmed_retriever.search_vector(
                question,
                top_k=5
            )
        )

        if vector_results is None:

            vector_results = []

        # ------------------------------------------
        # STEP 5
        # EXPLICIT KG EVIDENCE
        # ------------------------------------------

        kg_evidence = []

        for entity in linked_entities:

            if entity.get(
                "status"
            ) != "linked":

                continue

            disease_name = entity.get(
                "linked_entity"
            )

            if not disease_name:
                continue

            evidence = (
                kg_retriever.get_evidence_for_disease(
                    disease_name
                )
            )

            if evidence:

                kg_evidence.extend(
                    evidence
                )

        # ------------------------------------------
        # STEP 6
        # RECONCILIATION
        # ------------------------------------------

        reconciliation_result = (
            reconciler.reconcile(
                question,
                kg_evidence,
                vector_results
            )
        )

        # ------------------------------------------
        # RESPONSE
        # ------------------------------------------

        return {

            "status": "success",

            "question": question,

            "recognized_entities": entities,

            "linked_entities": linked_entities,

            "kg_context": kg_context,

            "kg_evidence": kg_evidence,

            "pubmed_query":
                pubmed_result.get(
                    "query",
                    ""
                ),

            "pubmed_articles":
                pubmed_articles,

            "vector_results":
                vector_results,

            "reconciliation":
                reconciliation_result

        }

    except Exception as e:

        return {

            "status": "error",

            "error": str(e)

        }


# ==================================================
# MAIN MEDICAL QUESTION ENDPOINT
# ==================================================

@app.post("/ask")
def ask_medical_question(
    request: QuestionRequest
):

    question = request.question.strip()

    try:

        # ------------------------------------------
        # VALIDATION
        # ------------------------------------------

        if not question:

            return {

                "status": "error",

                "error":
                    "Question cannot be empty."

            }

        # ------------------------------------------
        # STEP 1
        # ENTITY RECOGNITION
        # ------------------------------------------

        entities = (
            entity_recognizer.recognize(
                question
            )
        )

        # ------------------------------------------
        # STEP 2
        # ENTITY LINKING
        # ------------------------------------------

        linked_entities = []

        for entity in entities.get(
            "diseases",
            []
        ):

            linked_entity = (
                entity_linker.link_entity(
                    entity
                )
            )

            linked_entities.append(
                linked_entity
            )

        # ------------------------------------------
        # STEP 3
        # KNOWLEDGE GRAPH RETRIEVAL
        # ------------------------------------------

        kg_context = []

        for entity in linked_entities:

            if entity.get(
                "status"
            ) != "linked":

                continue

            disease_name = entity.get(
                "linked_entity"
            )

            if not disease_name:
                continue

            results = (
                kg_retriever.get_disease_info(
                    disease_name
                )
            )

            if results:

                if isinstance(
                    results,
                    list
                ):

                    kg_context.extend(
                        results
                    )

                else:

                    kg_context.append(
                        results
                    )

        # ------------------------------------------
        # STEP 4
        # EXPLICIT KG EVIDENCE
        # ------------------------------------------

        kg_evidence = []

        for entity in linked_entities:

            if entity.get(
                "status"
            ) != "linked":

                continue

            disease_name = entity.get(
                "linked_entity"
            )

            if not disease_name:
                continue

            evidence = (
                kg_retriever.get_evidence_for_disease(
                    disease_name
                )
            )

            if evidence:

                kg_evidence.extend(
                    evidence
                )

        # ------------------------------------------
        # STEP 5
        # QUERY-AWARE PUBMED RETRIEVAL
        # ------------------------------------------

        pubmed_result = (
            pubmed_retriever.search_pubmed_for_question(
                question,
                entities,
                max_results=10
            )
        )

        pubmed_articles = (
            pubmed_result.get(
                "articles",
                []
            )
        )

        # ------------------------------------------
        # STEP 6
        # PUBMED INGESTION
        # ------------------------------------------

        if pubmed_articles:

            pubmed_retriever.ingest_articles(
                pubmed_articles
            )

        # ------------------------------------------
        # STEP 7
        # VECTOR RETRIEVAL
        # ------------------------------------------

        vector_results = (
            pubmed_retriever.search_vector(
                question,
                top_k=5
            )
        )

        if vector_results is None:

            vector_results = []

        # ------------------------------------------
        # STEP 8
        # EVIDENCE RECONCILIATION
        # ------------------------------------------

        reconciliation_result = (
            reconciler.reconcile(
                question,
                kg_evidence,
                vector_results
            )
        )

        # ------------------------------------------
        # STEP 9
        # R1-R5 VALIDATION
        # ------------------------------------------

        validation_result = (
            evidence_validator.validate(

                question=question,

                entities=entities,

                linked_entities=linked_entities,

                kg_evidence=kg_evidence,

                vector_evidence=vector_results,

                reconciliation=reconciliation_result

            )
        )

        # ------------------------------------------
        # STEP 10
        # EVIDENCE GATE
        # ------------------------------------------

        gate_result = (
            evidence_gate.evaluate(
                validation_result
            )
        )

        # ------------------------------------------
        # STEP 11
        # RESPONSE GENERATION
        # ------------------------------------------

        if gate_result.get(
            "allow_generation",
            False
        ):

            final_response = (
                medical_response_generator.generate(

                    question,

                    kg_context,

                    vector_results,

                    reconciliation_result

                )
            )

        else:

            final_response = {

                "answer": (
                    "The available evidence could not "
                    "be fully validated. A verified medical "
                    "answer was therefore not generated."
                ),

                "additional_information": [],

                "semantic_support": "",

                "reconciliation_status":
                    reconciliation_result.get(
                        "status",
                        "UNKNOWN"
                    ),

                "confidence": 0.0,

                "sources": []

            }

        # ------------------------------------------
        # HANDLE RESPONSE TYPES
        # ------------------------------------------

        if isinstance(
            final_response,
            str
        ):

            answer = final_response

            sources = []

            additional_information = []

            semantic_support = ""

            confidence = 0.0

        elif isinstance(
            final_response,
            dict
        ):

            answer = (
                final_response.get(
                    "answer",
                    ""
                )
            )

            sources = (
                final_response.get(
                    "sources",
                    []
                )
            )

            additional_information = (
                final_response.get(
                    "additional_information",
                    []
                )
            )

            semantic_support = (
                final_response.get(
                    "semantic_support",
                    ""
                )
            )

            confidence = (
                final_response.get(
                    "confidence",
                    0.0
                )
            )

        else:

            answer = str(
                final_response
            )

            sources = []

            additional_information = []

            semantic_support = ""

            confidence = 0.0

        # ------------------------------------------
        # FALLBACK ANSWER
        # ------------------------------------------

        if not answer:

            answer = (
                "No final answer could be generated "
                "from the retrieved medical information."
            )

        
        # ------------------------------------------
        # CLAIM-LEVEL AUDIT TRAIL
        # ------------------------------------------

        if gate_result.get("allow_generation", False):
            claim_audit = build_claim_audit(
                answer=answer,
                kg_evidence=kg_evidence,
                literature_evidence=vector_results,
                validation_result=validation_result,
            )
        else:
            claim_audit = {
                "audit_version": "0.2",
                "overall_validation_status": validation_result.get(
                    "status", "UNKNOWN"
                ),
                "claim_count": 0,
                "claims": [],
                "message": (
                    "Claim auditing was skipped because the evidence "
                    "gate blocked medical answer generation."
                ),
            }


        # ------------------------------------------
        # PIPELINE DATA
        # ------------------------------------------

        pipeline = {

            "entity_recognition": {

                "status":
                    "completed",

                "count":
                    len(
                        entities.get(
                            "diseases",
                            []
                        )
                    )

            },

            "entity_linking": {

                "status":
                    "completed",

                "count":
                    len(
                        linked_entities
                    )

            },

            "kg_retrieval": {

                "status":
                    (
                        "retrieved"
                        if kg_context
                        else "no_results"
                    ),

                "count":
                    len(
                        kg_context
                    )

            },

            "kg_evidence": {

                "status":
                    (
                        "retrieved"
                        if kg_evidence
                        else "no_results"
                    ),

                "count":
                    len(
                        kg_evidence
                    )

            },

            "pubmed_retrieval": {

                "status":
                    (
                        "retrieved"
                        if pubmed_articles
                        else "no_results"
                    ),

                "article_count":
                    len(
                        pubmed_articles
                    ),

                "query":
                    pubmed_result.get(
                        "query",
                        ""
                    )

            },

            "vector_retrieval": {

                "status":
                    (
                        "retrieved"
                        if vector_results
                        else "no_results"
                    ),

                "count":
                    len(
                        vector_results
                    )

            },

            "reconciliation": {

                "status":
                    reconciliation_result.get(
                        "status",
                        "UNKNOWN"
                    ),

                "confidence":
                    reconciliation_result.get(
                        "confidence",
                        0.0
                    )

            },

            "validation": {

                "status":
                    validation_result.get(
                        "status",
                        "UNKNOWN"
                    ),

                "passed_rules":
                    validation_result.get(
                        "passed_rules",
                        0
                    ),

                "failed_rules":
                    validation_result.get(
                        "failed_rules",
                        0
                    ),

                "pending_rules":
                    validation_result.get(
                        "pending_rules",
                        0
                    ),

                "total_rules":
                    validation_result.get(
                        "total_rules",
                        5
                    )

            },

            "evidence_gate": {

                "status":
                    gate_result.get(
                        "status",
                        "UNKNOWN"
                    ),

                "allow_generation":
                    gate_result.get(
                        "allow_generation",
                        False
                    )

            },

            "output_generation": {

                "status":
                    (
                        "completed"
                        if gate_result.get(
                            "allow_generation",
                            False
                        )
                        else
                        "blocked_by_evidence_gate"
                    )

            }

        }

        # ------------------------------------------
        # FINAL API RESPONSE
        # ------------------------------------------

        return {

            "status":
                "success",

            "question":
                question,

            "answer":
                answer,

            "additional_information":
                additional_information,

            "semantic_support":
                semantic_support,

            "confidence":
                confidence,

            "recognized_entities":
                entities,

            "linked_entities":
                linked_entities,

            "kg_context":
                kg_context,

            "kg_evidence":
                kg_evidence,

            "pubmed_query":
                pubmed_result.get(
                    "query",
                    ""
                ),

            "pubmed_articles":
                pubmed_articles,

            "vector_results":
                vector_results,

            "reconciliation":
                reconciliation_result,

            "validation":
                validation_result,

            "evidence_gate":
                gate_result,

            "claim_audit": claim_audit,

            "kg_result_count":
                len(
                    kg_context
                ),

            "kg_evidence_count":
                len(
                    kg_evidence
                ),

            "vector_result_count":
                len(
                    vector_results
                ),

            "sources":
                sources,

            "pipeline":
                pipeline

        }

    except Exception as e:

        print(
            "ASK ENDPOINT ERROR:",
            str(e)
        )

        return {

            "status":
                "error",

            "error":
                str(e)

        }


# ==================================================
# SHUTDOWN
# ==================================================

@app.on_event("shutdown")
def shutdown():

    db.close()