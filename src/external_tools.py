# Two external data tools: DuckDuckGo for company context, Adzuna for live job listings.
# Both are opt-in via sidebar toggles -- they make network calls on every agent turn,
# which adds latency and can fail, so the default keeps them off.
# These are plain HTTP tools passed directly into the LangGraph agent's tool list.

import os

import requests

from src.logger import get_logger

_log = get_logger("careerfit.external")


def search_company(company_name: str) -> str:
    """Fetch a public summary of a company from DuckDuckGo's instant answer API.

    No API key needed. The tradeoff is that DDG's abstract field is sparse --
    it works well for large global companies and returns empty for most regional ones.
    The fallback message tells the agent to proceed with KB evidence only,
    so an empty result doesn't break the response.
    """
    try:
        # Search the bare company name -- adding suffixes like "company AI"
        # causes DuckDuckGo to miss the Wikipedia abstract entirely.
        response = requests.get(
            "https://api.duckduckgo.com/",
            params={
                "q": company_name,
                "format": "json",
                "no_redirect": "1",
                "no_html": "1",
                "skip_disambig": "1",
            },
            timeout=5,
        )
        data = response.json()
        abstract = data.get("AbstractText", "")
        abstract_url = data.get("AbstractURL", "")
        abstract_source = data.get("AbstractSource", "")

        # Filter related topics: skip bare category names (no " - " separator)
        # and keep only ones with a real sentence after the dash.
        meaningful_related = []
        for r in data.get("RelatedTopics", []):
            if not isinstance(r, dict):
                continue
            text = r.get("Text", "")
            # DDG formats related topics as "Label - Description"
            # Pure category pages have no " - " so we skip them.
            if " - " in text and len(text) > 40:
                meaningful_related.append(text[:250])
            if len(meaningful_related) >= 4:
                break

        if abstract:
            parts = [
                f"## {company_name}: Company Research",
                f"\n{abstract}",
            ]
            if abstract_url:
                parts.append(f"\nSource: {abstract_url}")
            if meaningful_related:
                parts.append("\n### Related context")
                for rel in meaningful_related:
                    parts.append(f"- {rel}")
            _log.info("company search succeeded for: %s", company_name)
            return "\n".join(parts)
        elif meaningful_related:
            _log.info("company search partial result for: %s", company_name)
            return (
                f"Limited public info found for {company_name}.\n"
                + "\n".join(f"- {r}" for r in meaningful_related)
            )
        else:
            _log.info("company search returned no results for: %s", company_name)
            return (
                f"No public summary found for {company_name}. "
                "Base the positioning on the knowledge base only."
            )

    except Exception as exc:
        _log.warning("company search failed for %s: %s", company_name, exc)
        return "Company search unavailable right now. Base the positioning on the knowledge base only."


def search_jobs(job_title: str, location: str = "Berlin") -> str:
    """Fetch up to 5 live job listings from Adzuna for a given role title and location.

    Requires ADZUNA_APP_ID and ADZUNA_APP_KEY in .env; returns a setup message
    if keys are missing rather than raising an error. Free tier at
    developer.adzuna.com covers demo-level usage.
    """
    app_id = os.getenv("ADZUNA_APP_ID", "")
    app_key = os.getenv("ADZUNA_APP_KEY", "")

    if not app_id or not app_key:
        return (
            "Live job search is not configured yet.\n"
            "To enable it: get free API keys at https://developer.adzuna.com/ "
            "and add ADZUNA_APP_ID and ADZUNA_APP_KEY to your .env file."
        )

    try:
        response = requests.get(
            "https://api.adzuna.com/v1/api/jobs/de/search/1",
            params={
                "app_id": app_id,
                "app_key": app_key,
                "what": job_title,
                "where": location,
                "results_per_page": 5,
            },
            timeout=8,
        )
        data = response.json()
        jobs = data.get("results", [])

        if not jobs:
            return f"No live listings found for '{job_title}' in {location} right now."

        lines = [f"Live listings for '{job_title}' in {location}:\n"]
        for job in jobs:
            title = job.get("title", "Role")
            company = job.get("company", {}).get("display_name", "Company")
            description = job.get("description", "")[:150]
            url = job.get("redirect_url", "")
            lines.append(f"**{title}** at {company}")
            lines.append(f"{description}...")
            lines.append(f"{url}\n")

        _log.info(
            "job search returned %d results for: %s in %s",
            len(jobs), job_title, location,
        )
        return "\n".join(lines)

    except Exception as exc:
        _log.warning("job search failed: %s", exc)
        return "Job search failed. Try again or paste a job description directly."


if __name__ == "__main__":
    # load_dotenv so ADZUNA keys are available when running this file directly
    from dotenv import load_dotenv
    load_dote