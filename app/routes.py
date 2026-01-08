from flask import Blueprint, jsonify, request

from .services import classify_incident, suggest_runbook_section


bp = Blueprint("api", __name__)


@bp.route("/health", methods=["GET"])
def health() -> tuple[dict, int]:
    return {"status": "ok"}, 200


@bp.route("/incidents/classify", methods=["POST"])
def classify() -> tuple[dict, int]:
    payload = request.get_json(force=True) or {}
    title = payload.get("title", "")
    description = payload.get("description", "")

    incident_type, confidence = classify_incident(title=title, description=description)

    return jsonify({
        "incident_type": incident_type,
        "confidence": confidence,
    }), 200


@bp.route("/incidents/suggest-runbook", methods=["POST"])
def suggest_runbook() -> tuple[dict, int]:
    payload = request.get_json(force=True) or {}
    query = payload.get("query", "")

    suggestion = suggest_runbook_section(query)

    # Flatten suggestion fields at the top level so the frontend can
    # read `answer`, `backend`, etc. directly without drilling into a
    # nested object.
    response = {"query": query}
    if isinstance(suggestion, dict):
        response.update(suggestion)
    else:
        response["answer"] = str(suggestion)

    return jsonify(response), 200
