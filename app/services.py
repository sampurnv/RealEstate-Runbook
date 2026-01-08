"""Core AI/ML/LangChain service stubs.

This module is intentionally minimal and framework-agnostic so you can
plug in real models later (transformers, LangChain chains, etc.).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Tuple

# LangChain-related imports are done lazily inside helper functions so that
# the service can still run in environments where LangChain or OpenAI are not
# configured. This keeps the module importable even without those extras.

BASE_DIR = Path(__file__).resolve().parents[1]
RUNBOOK_PATH = BASE_DIR / "runbook" / "real_estate_marketing_runbook.md"


# Simple rule-based classifier placeholder; replace with DL/NLP model later.
INCIDENT_KEYWORDS = {
    "lead_drop": ["lead", "lead volume", "no leads", "fewer leads"],
    "listing_issue": ["listing", "property", "mls", "idx"],
    "ad_issue": ["campaign", "ad", "cpc", "cpl", "impressions"],
    "email_sms_issue": ["email", "sms", "notification", "twilio", "sendgrid"],
    "website_issue": ["website", "landing page", "page speed", "500 error"],
    "analytics_issue": ["dashboard", "kpi", "analytics", "report"],
}


_QA_CHAIN = None  # type: ignore[var-annotated]
_QA_ERROR: str | None = None


class _SimpleQAChain:
    """Minimal QA helper that mimics LangChain's .invoke pattern.

    It uses a retriever to get relevant runbook chunks and an LLM to
    answer the user's query based on those chunks.
    """

    def __init__(self, retriever, llm) -> None:  # type: ignore[no-untyped-def]
        self._retriever = retriever
        self._llm = llm

    def invoke(self, inputs):  # type: ignore[no-untyped-def]
        if isinstance(inputs, dict):
            query = inputs.get("query", "")
        else:
            query = str(inputs)

        docs = self._retriever.get_relevant_documents(query)
        context = "\n\n".join(d.page_content for d in docs)

        prompt = (
            "You are an assistant helping to resolve incidents in "
            "real estate marketing systems. Use the provided runbook "
            "context to suggest concrete next steps.\n\n"  # noqa: E501
            "Runbook context:\n" + context + "\n\n"  # noqa: E501
            "Incident description: " + query + "\n\n"  # noqa: E501
            "Answer with a concise, step-by-step action plan."
        )

        response = self._llm.invoke(prompt)
        # ChatOpenAI / ChatOllama responses usually have .content
        text = getattr(response, "content", None) or str(response)
        return {"result": text}


def classify_incident(title: str, description: str) -> Tuple[str, float]:
    """Very simple keyword-based classifier.

    Replace this with a deep-learning/NLP model later (e.g. fine-tuned
    transformer using HuggingFace, spaCy, etc.).
    """

    text = f"{title} {description}".lower()
    best_label = "unknown"
    best_score = 0.0

    for label, keywords in INCIDENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_label = label
            best_score = float(score)

    confidence = min(1.0, best_score / 3.0) if best_score > 0 else 0.0
    return best_label, confidence


def _load_runbook_text() -> str:
    if not RUNBOOK_PATH.exists():
        return ""
    return RUNBOOK_PATH.read_text(encoding="utf-8")

def _init_qa_chain() -> None:
    """Initialise a QA helper over the runbook markdown.

    This uses:
    - sentence-transformers/all-MiniLM-L6-v2 embeddings via
      langchain_community.embeddings.HuggingFaceEmbeddings
    - FAISS in-memory vector store
    - LLM selection:
        * ChatOpenAI if OPENAI_API_KEY is set
        * otherwise ChatOllama pointing at a local server
          (default base URL http://127.0.0.1:11434)

    On any failure, the error is stored in _QA_ERROR and the rest of the
    service can continue to function using the rule-based fallback.
    """

    global _QA_CHAIN, _QA_ERROR

    if _QA_CHAIN is not None or _QA_ERROR is not None:
        return

    text = _load_runbook_text()
    if not text:
        _QA_ERROR = "runbook file missing"
        return

    try:
        from langchain_openai import ChatOpenAI
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS

        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
        except ImportError:  # fallback for older langchain versions
            from langchain.text_splitter import (  # type: ignore[assignment]
                RecursiveCharacterTextSplitter,
            )

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
        )
        docs = splitter.create_documents([text])

        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vectorstore = FAISS.from_documents(docs, embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

        # Choose LLM backend: OpenAI (if key present) or local Ollama.
        llm = None
        openai_error: str | None = None

        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                llm = ChatOpenAI(temperature=0.0)
            except Exception as exc:  # pragma: no cover - defensive
                openai_error = str(exc)

        if llm is None:
            from langchain_community.chat_models import ChatOllama

            try:
                llm = ChatOllama(
                    model=os.getenv("OLLAMA_MODEL", "llama3.1"),
                    base_url=os.getenv(
                        "OLLAMA_BASE_URL", "http://127.0.0.1:11434"
                    ),
                )
            except Exception as exc:  # pragma: no cover - defensive
                if openai_error:
                    _QA_ERROR = (
                        "Failed to init ChatOpenAI ("
                        + openai_error
                        + ") and ChatOllama ("
                        + str(exc)
                        + ")"
                    )
                else:
                    _QA_ERROR = f"Failed to init ChatOllama ({exc})"
                return

        _QA_CHAIN = _SimpleQAChain(retriever=retriever, llm=llm)
    except Exception as exc:  # pragma: no cover - defensive
        _QA_ERROR = str(exc)


def _suggest_runbook_section_rule_based(query: str) -> dict:
    """Original rule-based section suggester using simple keyword mapping."""

    runbook_text = _load_runbook_text()

    if not runbook_text:
        return {"section": "", "reason": "runbook file missing", "excerpt": ""}

    # Map labels to section headers in the markdown.
    section_map = {
        "lead_drop": "## 2. Lead Volume Crash / Drop in Inbound Leads",
        "listing_issue": "## 3. Listings Missing / Wrong / Outdated",
        "ad_issue": "## 4. Ad Campaign / Performance Issues",
        "email_sms_issue": "## 5. Email/SMS Campaign or Notification Failures",
        "website_issue": "## 6. Website / Landing Page Issues",
        "analytics_issue": "## 7. Data/Analytics/Reporting Issues",
    }

    label, confidence = classify_incident(query, "")
    header = section_map.get(label, "")

    if not header:
        return {
            "section": "",
            "reason": "no matching section; extend runbook or improve model",
            "excerpt": "",
            "incident_type": label,
            "confidence": confidence,
        }

    start = runbook_text.find(header)
    if start == -1:
        return {
            "section": header,
            "reason": "section header not found in markdown; check runbook file",
            "excerpt": "",
            "incident_type": label,
            "confidence": confidence,
        }

    # Extract up to the next section header as a simple excerpt.
    next_header_pos = runbook_text.find("\n## ", start + len(header))
    if next_header_pos == -1:
        excerpt = runbook_text[start:]
    else:
        excerpt = runbook_text[start:next_header_pos]

    return {
        "section": header,
        "incident_type": label,
        "confidence": confidence,
        "excerpt": excerpt.strip(),
    }


def suggest_runbook_section(query: str) -> dict:
    """Suggest actions using LangChain RetrievalQA over the runbook.

    Behaviour:
    - If LangChain + OpenAI are available and the QA chain initialises,
      uses RetrievalQA to answer the query based on the markdown.
    - Otherwise falls back to the original rule-based section lookup.
    """

    global _QA_CHAIN, _QA_ERROR

    _init_qa_chain()

    label, confidence = classify_incident(query, "")

    if _QA_CHAIN is not None:
        try:
            result = _QA_CHAIN.invoke({"query": query})  # type: ignore[misc]
            answer_text = (
                result.get("result")
                or result.get("answer")
                or str(result)
            )
            return {
                "backend": "langchain_retrievalqa",
                "incident_type": label,
                "confidence": confidence,
                "answer": answer_text,
            }
        except Exception as exc:  # pragma: no cover - defensive
            _QA_ERROR = str(exc)

    # Fallback: rule-based mapping
    rb = _suggest_runbook_section_rule_based(query)
    rb.setdefault("incident_type", label)
    rb.setdefault("confidence", confidence)

    # Derive a plain-text answer from the excerpt/reason so the UI can
    # always display step-by-step text instead of raw JSON.
    if rb.get("excerpt"):
        rb["answer"] = rb["excerpt"]
    elif rb.get("reason"):
        rb["answer"] = rb["reason"]

    rb["backend"] = "rule_based"
    if _QA_ERROR:
        rb["langchain_error"] = _QA_ERROR
    return rb
