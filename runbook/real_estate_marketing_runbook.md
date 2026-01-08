# Real Estate Marketing Incident Runbook

This document describes the standardized procedures for detecting, triaging, diagnosing, resolving, and learning from incidents affecting real estate marketing systems.

## 1. Incident Lifecycle

1. **Detect**
   - Inputs: alerts, tickets, dashboards, ad-platform anomalies, agent/client complaints.
2. **Triage**
   - Classify incident type and severity.
3. **Diagnose**
   - Collect context, logs, metrics, and recent changes.
4. **Resolve**
   - Apply the relevant procedure (sections 2–7).
5. **Communicate**
   - Notify stakeholders with status and ETA.
6. **Post-Incident**
   - Capture root cause and improvements.

## 2. Lead Volume Crash / Drop in Inbound Leads

**Symptoms**
- Sudden drop in new leads/day from website, landing pages, portals, or ads.

**Steps**
1. Verify data vs reality (compare sessions vs leads by channel).
2. Check forms and submissions (front-end + Flask endpoints).
3. Check webhooks/CRM integrations and provider errors.
4. Check ad/portal campaign status and budgets.
5. Fix broken endpoints, webhooks, tracking, or campaign configs.
6. Add/adjust monitoring and anomaly alerts.

## 3. Listings Missing / Wrong / Outdated

**Symptoms**
- Missing, incorrect, or outdated property information on the site or portals.

**Steps**
1. Determine scope (single listing, office, MLS, or global).
2. Check MLS/IDX/other feed ingestion times and errors.
3. Validate field mappings between source and internal schema.
4. Check portal syndication feed generation and ingestion.
5. Fix credentials, schema mappings, or failed feeds and re-sync.
6. Add completeness checks (counts by MLS vs site/portal).

## 4. Ad Campaign / Performance Issues

**Symptoms**
- Drops in impressions/clicks, rising CPL, or non-serving campaigns.

**Steps**
1. Verify campaign status, budgets, and policy compliance.
2. Validate conversion tracking (pixels, tags, server-side events).
3. Check recent changes to audiences, bids, creatives, or landing pages.
4. Roll back or correct harmful changes; repair tracking.
5. Enable ongoing performance and anomaly monitoring.

## 5. Email/SMS Campaign or Notification Failures

**Symptoms**
- Campaigns or notifications not sending or spiking bounces.

**Steps**
1. Check provider status, quotas, and bounce/complaint reports.
2. Check background jobs/queues and application logs.
3. Validate templates and personalization logic.
4. Fix failing jobs or templates, and address reputation issues.
5. Add alerts for deliverability and queue health.

## 6. Website / Landing Page Issues

**Symptoms**
- Outages, slowness, broken journeys, high bounce/abandon.

**Steps**
1. Check HTTP error rates and infrastructure health.
2. Analyze performance metrics and recent code/content changes.
3. Test key user journeys (search → listing → form, etc.).
4. Roll back or fix defective deploys, JS errors, or heavy assets.
5. Add synthetic monitoring for key flows.

## 7. Data/Analytics/Reporting Issues

**Symptoms**
- Dashboards do not match reality; KPIs missing or wrong.

**Steps**
1. Verify ETL/data pipeline job status and schema changes.
2. Compare KPI definitions between business and reports.
3. Fix ETL logic, schema mappings, or definitions.
4. Add data freshness and consistency checks.

## 8. AI-Enhanced Operations (Conceptual)

- Use an incident classifier model to map incidents to sections above.
- Use a retrieval-based LLM (e.g., via LangChain) to:
  - Find the most relevant runbook section.
  - Generate a suggested action plan for responders.
- Use anomaly detection models on leads, listings, and campaign metrics to trigger incidents early.
