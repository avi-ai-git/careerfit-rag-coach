# The four core career tools plus two optional external tools for company research
# and job search. All four career tools share _search_impl so retrieval always
# runs before any LLM call -- skipping retrieval was the original Sprint 1 gap.

from langchain_core.tools import tool

from src.llm import get_llm
from src.logger import get_logger
from src.external_tools import search_company, search_jobs
from src.prompts import (
    JOB_FIT_PROMPT,
    APPLICATION_POSITIONING_PROMPT,
    INTERVIEW_PREP_PROMPT,
)
from src.query_translation import translate_query
from src.retriever import retrieve_chunks, format_context

_log = get_logger("careerfit.tools")

# Module-level variable so the three structured-output tools use the same model
# the user selected in the sidebar. agent.py calls set_active_model() before
# invoking the agent so every tool call in that turn uses the right model.
_active_model = None


def set_active_model(model_name):
    """Called by run_agent() before each invocation to propagate the sidebar model."""
    global _active_model
    _active_model = model_name


def _search_impl(query, exclude_doc_types=None):
    """Translate query to phrases, retrieve chunks across all phrases, deduplicate, format.

    Running multiple translated queries and merging results improves recall
    at the cost of more ChromaDB calls -- acceptable for a single-user app.
    Passes _active_model to translate_query so the expansion step uses the same
    model the user selected in the sidebar, not the hardcoded default.
    """
    queries = translate_query(query, model=_active_model)
    seen = set()
    all_chunks = []

    for q in queries:
        for chunk in retrieve_chunks(q, exclude_doc_types=exclude_doc_types):
            # dedup by first 100 chars -- full content comparison was slow and overkill
            key = chunk["content"][:100]
            if key not in seen:
                seen.add(key)
                all_chunks.append(chunk)

    _log.info("queries=%d unique_chunks=%d", len(queries), len(all_chunks))
    return format_context(all_chunks) if all_chunks else "No relevant evidence found."


@tool
def search_career_evidence(query: str) -> str:
    """Search the knowledge base and return relevant passages with source filenames.

    Call this before making any claim about the candidate's background.
    This is the only tool that searches without doc_type exclusions -- freeform
    questions should see all available evidence including test JDs.
    """
    try:
        return _search_impl(query)
    except Exception as exc:
        return f"Error searching knowledge base: {exc}"


@tool
def analyze_job_fit(job_description: str) -> str:
    """Analyze candidate fit for a job description and return a structured markdown report.

    Report includes fit score (0-100), fit level, matched strengths with citations,
    honest gaps, and a positioning angle. test_job_descriptions are excluded from
    retrieval here because they pollute the context with unrelated role vocabulary.
    """
    try:
        context = _search_impl(job_description, exclude_doc_types=["test_job_descriptions"])
        # Use _active_model so the tool honours the sidebar model selection.
        # set_active_model() is called by run_agent() before each invocation.
        llm = get_llm(model=_active_model)
        response = llm.invoke(
            JOB_FIT_PROMPT.format(job_description=job_description, context=context)
        )
        return response.content
    except Exception as exc:
        return f"Error analyzing job fit: {exc}"


@tool
def generate_application_positioning(job_description: str) -> str:
    """Generate a positioning paragraph, 5 proof points, and a list of claims to avoid.

    The claims-to-avoid section is intentional -- it prevents the LLM from inventing
    experience that isn't in the KB, which is the main failure mode for career AI tools.
    """
    try:
        context = _search_impl(job_description, exclude_doc_types=["test_job_descriptions"])
        llm = get_llm(model=_active_model)
        response = llm.invoke(
            APPLICATION_POSITIONING_PROMPT.format(
                job_description=job_description, context=context
            )
        )
        return response.content
    except Exception as exc:
        return f"Error generating application positioning: {exc}"


@tool
def generate_interview_prep(input_text: str) -> str:
    """Return 10 interview questions with STAR answer notes drawn from KB evidence.

    Questions are grounded in retrieved passages, not general interview advice.
    Each answer note cites a source file so the candidate can verify the claim.
    """
    try:
        context = _search_impl(input_text, exclude_doc_types=["test_job_descriptions"])
        llm = get_llm(model=_active_model)
        response = llm.invoke(
            INTERVIEW_PREP_PROMPT.format(job_description=input_text, context=context)
        )
        return response.content
    except Exception as exc:
        return f"Error generating interview prep: {exc}"


@tool
def company_research(company_name: str) -> str:
    """Look up public information about a company the user is applying to.

    Only call this when the user explicitly names a company.
    If no company is mentioned, skip it -- generic company info adds noise.
    """
    return search_company(company_name)


@tool
def find_job_listings(job_title: str) -> str:
    """Search for live job listings matching a role title in Berlin.

    Only call this when the user wants to find jobs, not when a JD was already pasted.
    Returns a setup message if Adzuna keys are not configured.
    """
    return search_jobs(job_title)


def get_tools(
    enable_company_research=False,
    enable_job_search=False,
    mode="Ask Career Base",
):
    """Return the tool list for the agent.

    Base 4 tools are always included. Optional external tools are opt-in via sidebar toggles.
    find_job_listings is only added in Ask Career Base mode -- in the three JD modes
    the user has already pasted a job description, so searching for listings adds no value
    and confuses the agent about which tool to call.
    company_research is available in all modes because the user may name a company
    alongside any type of request.
    """
    tools = [
        search_career_evidence,
        analyze_job_fit,
        generate_application_positioning,
        generate_interview_prep,
    ]
    if enable_company_research:
        tools.append(company_research)
    if enable_job_search and mode == "Ask Career Base":
        tools.append(find_job_listings)
    return tools


if __name__ == "__main__":
    tools = get_tools()
    print(f"Tools loaded: {len(tools)}\n")
    for t in tools:
        first_line = t.description.strip().splitlines()[0]
        print(f"  {t.name}")
        print(f"    {first_line}")
