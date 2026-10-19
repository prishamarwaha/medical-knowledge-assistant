const questionInput = document.getElementById("questionInput");
const askButton = document.getElementById("askButton");
const results = document.getElementById("results");
const loading = document.getElementById("loading");
const errorBox = document.getElementById("errorBox");

const directAnswer = document.getElementById("directAnswer");
const kgInformation = document.getElementById("kgInformation");
const vectorEvidence = document.getElementById("vectorEvidence");

const reconciliationStatus = document.getElementById("reconciliationStatus");
const reconciliationDescription = document.getElementById("reconciliationDescription");

const confidenceValue = document.getElementById("confidenceValue");
const confidenceCircle = document.getElementById("confidenceCircle");

const kgTermCount = document.getElementById("kgTermCount");
const vectorTermCount = document.getElementById("vectorTermCount");
const matchingTermCount = document.getElementById("matchingTermCount");
const matchingTerms = document.getElementById("matchingTerms");

const sourcesContainer = document.getElementById("sourcesContainer");
const pipeline = document.getElementById("pipeline");


askButton.addEventListener("click", askQuestion);


questionInput.addEventListener("keydown", function (event) {

    if (event.key === "Enter") {
        askQuestion();
    }

});


async function askQuestion() {

    const question = questionInput.value.trim();


    if (!question) {

        showError("Please enter a medical question.");

        return;
    }


    console.log("Sending question:", question);


    results.classList.add("hidden");

    errorBox.classList.add("hidden");

    loading.classList.remove("hidden");


    askButton.disabled = true;

    askButton.textContent = "Processing...";


    try {

        const response = await fetch(
            "http://127.0.0.1:8000/ask",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    question: question
                })
            }
        );


        console.log("Response status:", response.status);


        if (!response.ok) {

            throw new Error(
                "Server error: " + response.status
            );

        }


        const data = await response.json();


        console.log("Backend response:", data);


        if (
            data.status &&
            data.status !== "success"
        ) {

            throw new Error(
                data.error ||
                "Unable to process question."
            );

        }


        renderResults(data);


        results.classList.remove("hidden");

    }

    catch (error) {

        console.error("Frontend error:", error);


        showError(
            error.message ||
            "Unable to connect to the backend."
        );

    }

    finally {

        loading.classList.add("hidden");


        askButton.disabled = false;


        askButton.textContent = "Get Answer";

    }

}



function renderResults(data) {
    console.log("Rendering results...", data);

    renderDirectAnswer(
        data.answer || data.direct_answer || data.response
    );

    renderKGInformation(
        data.kg_context || data.kg_results || data.knowledge_graph || []
    );

    renderVectorEvidence(
        data.vector_results || data.vector_evidence || []
    );

    renderReconciliation(data.reconciliation || {});
    renderSources(data.sources || []);
    renderPipeline(data.pipeline || {});

    // Newly connected backend fields
    renderEvidenceGate(data.evidence_gate || {});
    renderValidation(data.validation || {});
    renderKGTriples(data.kg_evidence || []);
    renderPubMedArticles(
        data.pubmed_articles || [],
        data.pubmed_query || ""
    );
    renderClaimAudit(data.claim_audit || {});
}


function renderDirectAnswer(answer) {

    if (!directAnswer) {
        return;
    }


    directAnswer.textContent =
        answer ||
        "No answer could be generated.";

}


function renderKGInformation(kgContext) {

    if (!kgInformation) {
        return;
    }


    kgInformation.innerHTML = "";


    if (!Array.isArray(kgContext)) {

        if (kgContext && typeof kgContext === "object") {
            kgContext = [kgContext];
        }

        else {
            kgContext = [];
        }

    }


    if (kgContext.length === 0) {

        kgInformation.appendChild(

            createInfoCard(
                "Knowledge Graph",
                "No structured medical information was retrieved.",
                "general",
                true
            )

        );

        return;
    }


    const item = kgContext[0];


    const symptoms = getField(
        item,
        [
            "Symptoms",
            "symptoms",
            "Associated Symptoms"
        ]
    );


    const tests = getField(
        item,
        [
            "Tests",
            "tests",
            "Diagnostic Tests"
        ]
    );


    const drugs = getField(
        item,
        [
            "Drugs",
            "drugs",
            "Treatment",
            "treatment",
            "Treatment Options"
        ]
    );


    const risks = getField(
        item,
        [
            "Risk Factors",
            "risk_factors",
            "risks"
        ]
    );


    const complications = getField(
        item,
        [
            "Complications",
            "complications",
            "Possible Complications"
        ]
    );


    if (symptoms) {

        kgInformation.appendChild(

            createInfoCard(
                "Associated Symptoms",
                symptoms,
                "symptoms"
            )

        );

    }


    if (tests) {

        kgInformation.appendChild(

            createInfoCard(
                "Diagnostic Tests",
                tests,
                "tests"
            )

        );

    }


    if (drugs) {

        kgInformation.appendChild(

            createInfoCard(
                "Treatment Options",
                drugs,
                "treatment"
            )

        );

    }


    if (risks) {

        kgInformation.appendChild(

            createInfoCard(
                "Risk Factors",
                risks,
                "risk"
            )

        );

    }


    if (complications) {

        kgInformation.appendChild(

            createInfoCard(
                "Possible Complications",
                complications,
                "complications",
                true
            )

        );

    }


    if (kgInformation.children.length === 0) {

        Object.entries(item).forEach(
            function ([key, value]) {

                if (
                    typeof value === "string" ||
                    Array.isArray(value)
                ) {

                    kgInformation.appendChild(

                        createInfoCard(
                            formatTitle(key),
                            Array.isArray(value)
                                ? value.join(", ")
                                : value,
                            "general"
                        )

                    );

                }

            }
        );

    }

}


function getField(object, possibleFields) {

    if (!object) {
        return "";
    }


    for (const field of possibleFields) {

        const value = object[field];


        if (
            Array.isArray(value) &&
            value.length > 0
        ) {

            return value.join(", ");

        }


        if (
            typeof value === "string" &&
            value.trim()
        ) {

            return value;

        }

    }


    return "";

}


function createInfoCard(
    title,
    content,
    type,
    fullWidth = false
) {

    const card =
        document.createElement("div");


    card.className =
        "info-card " + type;


    if (fullWidth) {

        card.classList.add(
            "full-width"
        );

    }


    const titleElement =
        document.createElement("div");


    titleElement.className =
        "info-title";


    titleElement.textContent =
        title;


    const contentElement =
        document.createElement("div");


    contentElement.className =
        "info-content";


    contentElement.textContent =
        content;


    card.appendChild(titleElement);

    card.appendChild(contentElement);


    return card;

}


function renderVectorEvidence(vectorResults) {

    if (!vectorEvidence) {
        return;
    }


    vectorEvidence.innerHTML = "";


    if (!Array.isArray(vectorResults)) {

        if (vectorResults) {
            vectorResults = [vectorResults];
        }

        else {
            vectorResults = [];
        }

    }


    if (vectorResults.length === 0) {

        const evidence =
            document.createElement("div");


        evidence.className =
            "evidence-card";


        evidence.textContent =
            "No supporting semantic evidence was retrieved.";


        vectorEvidence.appendChild(
            evidence
        );


        return;

    }


    vectorResults.forEach(
        function (result, index) {

            const card =
                document.createElement("div");


            card.className =
                "evidence-card";


            const text =
                document.createElement("div");


            text.className =
                "evidence-text";


            if (typeof result === "string") {

                text.textContent =
                    result;

            }

            else {

                text.textContent =
                    result.document ||
                    result.text ||
                    result.content ||
                    "No document content available.";

            }


            card.appendChild(text);


            if (
                typeof result === "object" &&
                result.distance !== undefined
            ) {

                const meta =
                    document.createElement("div");


                meta.className =
                    "evidence-meta";


                meta.textContent =
                    "Semantic Result " +
                    (index + 1) +
                    " | Distance: " +
                    result.distance;


                card.appendChild(meta);

            }


            vectorEvidence.appendChild(
                card
            );

        }
    );

}



function renderReconciliation(reconciliation) {
    reconciliation = reconciliation || {};

    const status = reconciliation.status || "UNKNOWN";
    const comparisons = Array.isArray(reconciliation.comparisons)
        ? reconciliation.comparisons
        : [];

    if (reconciliationStatus) {
        reconciliationStatus.textContent = formatStatus(status);
    }

    if (reconciliationDescription) {
        reconciliationDescription.textContent =
            reconciliation.reason ||
            getStatusDescription(status);
    }

    // Do not invent a confidence score.
    const confidence = reconciliation.confidence;

    if (confidenceValue) {
        confidenceValue.textContent =
            typeof confidence === "number"
                ? `${Math.round((confidence > 1 ? confidence / 100 : confidence) * 100)}%`
                : "N/A";
    }

    if (confidenceCircle) {
        const percentage = typeof confidence === "number"
            ? Math.max(0, Math.min(100,
                Math.round((confidence > 1 ? confidence / 100 : confidence) * 100)))
            : 0;

        confidenceCircle.style.background =
            `conic-gradient(#6fe0c4 0deg, #69d7ff ${percentage * 3.6}deg, rgba(255,255,255,0.1) ${percentage * 3.6}deg)`;
    }

    if (kgTermCount) {
        kgTermCount.textContent = reconciliation.kg_evidence_count ?? 0;
    }

    if (vectorTermCount) {
        vectorTermCount.textContent = reconciliation.vector_evidence_count ?? 0;
    }

    const terms = [
        ...new Set(
            comparisons.flatMap(comparison =>
                Array.isArray(comparison.matching_terms)
                    ? comparison.matching_terms
                    : []
            )
        )
    ];

    if (matchingTermCount) {
        matchingTermCount.textContent = terms.length;
    }

    if (matchingTerms) {
        matchingTerms.replaceChildren();

        if (terms.length === 0) {
            const empty = document.createElement("span");
            empty.className = "term";
            empty.textContent = "No matching terms returned";
            matchingTerms.appendChild(empty);
        } else {
            terms.forEach(term => {
                const element = document.createElement("span");
                element.className = "term";
                element.textContent = term;
                matchingTerms.appendChild(element);
            });
        }
    }

    // Show which KG fact was paired with which vector result.
    let comparisonContainer = document.getElementById(
        "reconciliationComparisons"
    );

    if (!comparisonContainer) {
        comparisonContainer = document.createElement("div");
        comparisonContainer.id = "reconciliationComparisons";
        comparisonContainer.className = "evidence-container";

        const parent = reconciliationStatus?.closest(".glass-card");
        if (parent) parent.appendChild(comparisonContainer);
    }

    if (comparisonContainer) {
        comparisonContainer.replaceChildren();

        const heading = document.createElement("h3");
        heading.textContent =
            `Evidence comparisons (${comparisons.length})`;
        comparisonContainer.appendChild(heading);

        comparisons.forEach(comparison => {
            const card = document.createElement("div");
            card.className = "evidence-card";

            const fact = document.createElement("strong");
            fact.textContent =
                `${comparison.subject || "Unknown"} — ` +
                `${comparison.relation || "UNKNOWN"} — ` +
                `${comparison.object || "Unknown"}`;

            const detail = document.createElement("p");
            detail.className = "evidence-meta";
            detail.textContent =
                `KG: ${comparison.kg_evidence_id || "Unknown"} | ` +
                `Vector: ${comparison.vector_evidence_id || "Unknown"} | ` +
                `Overlap: ${comparison.overlap ?? "N/A"}`;

            card.append(fact, detail);
            comparisonContainer.appendChild(card);
        });
    }
}



function formatStatus(status) {

    return String(status)
        .replaceAll("_", " ")
        .toUpperCase();

}


function formatTitle(title) {

    return String(title)
        .replaceAll("_", " ")
        .replace(/\b\w/g, function (letter) {
            return letter.toUpperCase();
        });

}


function getStatusDescription(status) {

    const normalized =
        String(status).toUpperCase();


    if (normalized === "AGREEMENT") {

        return (
            "The Knowledge Graph and semantic retrieval " +
            "provide aligned evidence for this query."
        );

    }


    if (
        normalized === "PARTIAL_AGREEMENT"
    ) {

        return (
            "The two retrieval systems share some " +
            "supporting evidence but are not fully aligned."
        );

    }


    if (
        normalized === "NO_AGREEMENT"
    ) {

        return (
            "The Knowledge Graph and semantic retrieval " +
            "do not currently show sufficient evidence alignment."
        );

    }


    return (
        "Evidence reconciliation information is available " +
        "after comparing both retrieval systems."
    );

}


function renderSources(sources) {

    if (!sourcesContainer) {
        return;
    }


    sourcesContainer.innerHTML = "";


    if (!Array.isArray(sources)) {

        if (sources) {
            sources = [sources];
        }

        else {
            sources = [];
        }

    }


    sources.forEach(
        function (source) {

            const sourceCard =
                document.createElement("div");


            sourceCard.className =
                "source-card";


            if (typeof source === "string") {

                sourceCard.textContent =
                    source;

            }

            else {

                sourceCard.textContent =
                    source.name ||
                    source.source ||
                    JSON.stringify(source);

            }


            sourcesContainer.appendChild(
                sourceCard
            );

        }
    );

}



function renderPipeline(pipelineData) {
    if (!pipeline) return;

    pipeline.replaceChildren();

    const steps = [
        ["Entity Recognition", pipelineData.entity_recognition],
        ["Entity Linking", pipelineData.entity_linking],
        ["Knowledge Graph Retrieval", pipelineData.kg_retrieval],
        ["KG Evidence Extraction", pipelineData.kg_evidence],
        ["PubMed Retrieval", pipelineData.pubmed_retrieval],
        ["Vector Retrieval", pipelineData.vector_retrieval],
        ["Evidence Reconciliation", pipelineData.reconciliation],
        ["Validation Rules R1–R5", pipelineData.validation],
        ["Evidence Gate", pipelineData.evidence_gate],
        ["Output Generation", pipelineData.output_generation]
    ];

    steps.forEach(([titleText, stepData], index) => {
        const card = document.createElement("div");
        card.className = "pipeline-step";

        const number = document.createElement("div");
        number.className = "pipeline-number";
        number.textContent = `STEP ${index + 1}`;

        const title = document.createElement("div");
        title.className = "pipeline-title";
        title.textContent = titleText;

        const status = document.createElement("div");
        status.className = "pipeline-status";

        status.textContent = stepData?.status
            ? formatStatus(stepData.status)
            : "NOT RETURNED";

        const detail = document.createElement("p");
        detail.className = "metric-description";

        if (stepData?.count !== undefined) {
            detail.textContent = `Count: ${stepData.count}`;
        } else if (stepData?.article_count !== undefined) {
            detail.textContent = `Articles: ${stepData.article_count}`;
        } else if (stepData?.allow_generation !== undefined) {
            detail.textContent = stepData.allow_generation
                ? "Generation permitted"
                : "Generation blocked";
        } else if (stepData?.failed_rules?.length) {
            detail.textContent =
                `Failed rules: ${stepData.failed_rules.join(", ")}`;
        } else if (stepData?.pending_rules?.length) {
            detail.textContent =
                `Pending rules: ${stepData.pending_rules.join(", ")}`;
        } else {
            detail.textContent = stepData?.reason || "";
        }

        card.append(number, title, status, detail);
        pipeline.appendChild(card);
    });
}



function showError(message) {

    console.error(message);


    if (errorBox) {

        errorBox.textContent =
            message;


        errorBox.classList.remove(
            "hidden"
        );

    }

}


function renderEvidenceGate(gate) {
    const statusEl = document.getElementById("evidenceGateStatus");
    const reasonEl = document.getElementById("evidenceGateReason");

    if (!statusEl || !reasonEl) return;

    const status = String(gate.status || "UNKNOWN").toUpperCase();

    statusEl.textContent =
        `${status} — Generation ${gate.allow_generation ? "allowed" : "blocked"}`;

    statusEl.dataset.status = status.toLowerCase();

    reasonEl.textContent =
        gate.reason || "No evidence-gate explanation was returned.";
}

function renderValidation(validation) {
    const container = document.getElementById("validationRules");
    if (!container) return;

    container.replaceChildren();

    const rules = validation.rules || {};

    ["R1", "R2", "R3", "R4", "R5"].forEach(ruleId => {
        const rule = rules[ruleId];
        const card = document.createElement("div");
        card.className = "info-card";

        const heading = document.createElement("div");
        heading.className = "info-title";
        heading.textContent = `${ruleId} — ${getRuleName(ruleId)}`;

        const status = document.createElement("div");
        status.className = "evidence-meta";
        status.textContent = rule
            ? String(rule.status || "UNKNOWN").toUpperCase()
            : "NOT RETURNED";

        const reason = document.createElement("p");
        reason.className = "info-content";
        reason.textContent = rule?.reason || "No rule result returned.";

        card.append(heading, status, reason);
        container.appendChild(card);
    });

    const summary = document.createElement("p");
    summary.className = "metric-description";
    summary.textContent =
        `Overall: ${validation.status || "UNKNOWN"} | ` +
        `Passed: ${validation.passed_rules ?? 0} | ` +
        `Failed: ${validation.failed_rules ?? 0} | ` +
        `Pending: ${validation.pending_rules ?? 0}`;

    container.prepend(summary);
}

function getRuleName(ruleId) {
    const names = {
        R1: "Entity Mapping",
        R2: "Ontology Validation",
        R3: "Relation Validation",
        R4: "Contradiction Screening",
        R5: "Evidence Support"
    };

    return names[ruleId] || "Validation Rule";
}


function renderKGTriples(evidence) {
    const container = document.getElementById("kgTriples");
    if (!container) return;

    container.replaceChildren();

    if (!Array.isArray(evidence) || evidence.length === 0) {
        container.textContent = "No KG evidence was returned.";
        return;
    }

    evidence.forEach(item => {
        const card = document.createElement("div");
        card.className = "evidence-card";

        const relation = document.createElement("strong");
        relation.textContent =
            `${item.subject || "Unknown"} → ` +
            `${item.relation || "UNKNOWN"} → ` +
            `${item.object || "Unknown"}`;

        const meta = document.createElement("div");
        meta.className = "evidence-meta";
        meta.textContent =
            `${item.evidence_id || "KG evidence"} | ` +
            `${item.source || "Source unavailable"}`;

        card.append(relation, meta);
        container.appendChild(card);
    });
}

function renderPubMedArticles(articles, query) {
    const container = document.getElementById("pubmedArticles");
    const queryEl = document.getElementById("pubmedQuery");

    if (queryEl) {
        queryEl.textContent = query
            ? `Search query: ${query}`
            : "No PubMed query returned.";
    }

    if (!container) return;

    container.replaceChildren();

    if (!Array.isArray(articles) || articles.length === 0) {
        container.textContent = "No PubMed articles were returned.";
        return;
    }

    articles.forEach(article => {
        const card = document.createElement("div");
        card.className = "evidence-card";

        const title = document.createElement("strong");
        title.textContent = article.title || "Untitled article";

        const meta = document.createElement("div");
        meta.className = "evidence-meta";
        meta.textContent = article.pmid
            ? `PMID: ${article.pmid}`
            : "PMID unavailable";

        const abstract = document.createElement("p");
        abstract.className = "evidence-text";
        abstract.textContent =
            article.abstract || "No abstract available.";

        card.append(title, meta, abstract);

        if (article.pmid) {
            const link = document.createElement("a");
            link.href =
                `https://pubmed.ncbi.nlm.nih.gov/${encodeURIComponent(article.pmid)}/`;
            link.target = "_blank";
            link.rel = "noopener noreferrer";
            link.textContent = "View on PubMed";

            card.appendChild(link);
        }

        container.appendChild(card);
    });
}


function renderClaimAudit(audit) {
    const summary = document.getElementById("claimAuditSummary");
    const container = document.getElementById("claimAuditResults");

    if (!summary || !container) return;

    container.replaceChildren();

    summary.textContent =
        `Audit version: ${audit.audit_version || "Unknown"} | ` +
        `Validation status: ${audit.overall_validation_status || "UNKNOWN"} | ` +
        `Claims audited: ${audit.claim_count ?? 0}`;

    if (audit.message) {
        const message = document.createElement("p");
        message.className = "metric-description";
        message.textContent = audit.message;
        container.appendChild(message);
    }

    const claims = Array.isArray(audit.claims) ? audit.claims : [];

    if (claims.length === 0) {
        if (!audit.message) {
            container.textContent = "No claim-level audit results returned.";
        }
        return;
    }

    claims.forEach((claim, index) => {
        const card = document.createElement("div");
        card.className = "evidence-card";

        const heading = document.createElement("strong");
        heading.textContent = `Claim ${index + 1}`;

        const text = document.createElement("p");
        text.className = "evidence-text";
        text.textContent = claim.claim || claim.text || "Claim text unavailable.";

        const status = document.createElement("div");
        status.className = "evidence-meta";
        status.textContent =
            `Support: ${claim.support_status || "UNKNOWN"} | ` +
            `Validation: ${claim.validation_status || "UNKNOWN"}`;

        card.append(heading, text, status);

        const candidates = Array.isArray(claim.candidates)
            ? claim.candidates
            : [];

        candidates.forEach(candidate => {
            const detail = document.createElement("p");
            detail.className = "metric-description";
            detail.textContent =
                `Evidence: ${candidate.evidence_id || candidate.id || "Unknown"} | ` +
                `Match score: ${candidate.match_score ?? "Unavailable"} | ` +
                `Status: ${candidate.support_status || "Unknown"}`;

            card.appendChild(detail);
        });

        container.appendChild(card);
    });
}
