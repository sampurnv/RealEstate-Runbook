# Real Estate Marketing Incident Runbook Platform

This workspace contains:
- A written incident runbook for real-estate marketing.
- A Flask-based API skeleton.
- AI hooks (LangChain-ready + ML/DL stubs) to classify incidents and suggest runbook steps.

Key paths:
- runbook/real_estate_marketing_runbook.md – main human runbook.
- app/ – Flask application with API and AI stubs.

Quick start:
- Create a virtualenv and install requirements: `pip install -r requirements.txt`.
- Run the app: `python -m app.wsgi`.
- Health check: GET http://localhost:5000/api/health
- Classify incident: POST http://localhost:5000/api/incidents/classify
	body: {"title": "...", "description": "..."}
- Suggest runbook section: POST http://localhost:5000/api/incidents/suggest-runbook
	body: {"query": "lead volume is down in portal X"}

LangChain RetrievalQA quick test (no HTTP):
- Set your OpenAI key: `export OPENAI_API_KEY="your-key"`.
- Run: `python test_runbook_qa.py "lead volume dropped on website and Facebook"`.
