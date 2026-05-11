# Entry point for the CareerFit RAG Coach Streamlit application

import os
import time
import uuid

import streamlit as st

from langgraph.checkpoint.memory import MemorySaver

from src.config import check_api_key, VECTORSTORE_DEMO_PATH
from src.agent import run_agent
from src.logger import get_logger
from src.security import sanitise_input
from src.cost_tracking import estimate_cost
from src.vector_store import build_vector_store
from src.utils import truncate_text

_log = get_logger("careerfit.app")

# ---------------------------------------------------------------------------
# Page config -- must be first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="CareerFit RAG Coach",
    page_icon="🎯",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Global CSS overrides
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Make the Coach / About tab labels larger and easier to click */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1.05rem;
        font-weight: 600;
        padding: 10px 28px;
        border-radius: 6px 6px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(255, 255, 255, 0.07);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Early-exit guardrails
# ---------------------------------------------------------------------------
if not VECTORSTORE_DEMO_PATH.exists():
    # Auto-build on first launch -- needed for Streamlit Cloud where the vectorstore
    # is not committed to git. Downloads the sentence-transformers model (~90 MB)
    # and embeds all knowledge base files. Takes about 60-90 seconds on first run only.
    with st.spinner("Setting up for the first time. This takes about a minute and only happens once..."):
        try:
            build_vector_store()
            _log.info("vectorstore built automatically on first launch")
        except Exception as e:
            st.error(
                f"Could not build the vector store: {e}\n\n"
                "Try running `python -m src.vector_store` locally first."
            )
            st.stop()

if not check_api_key():
    st.error(
        "OPENROUTER_API_KEY is missing. Add it to `.env`:\n\n"
        "```\nOPENROUTER_API_KEY=your-key-here\n```"
    )
    st.stop()

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "last_submit_time" not in st.session_state:
    st.session_state.last_submit_time = 0.0

if "request_count" not in st.session_state:
    st.session_state.request_count = 0

if "confirm_clear" not in st.session_state:
    st.session_state.confirm_clear = False

if "agent_memory" not in st.session_state:
    # Persistent MemorySaver; shared across all run_agent() calls in this session
    # so the agent can reference earlier turns (e.g. "repeat my last query").
    # Replaced with a fresh MemorySaver when the user clears the conversation.
    st.session_state.agent_memory = MemorySaver()

if "processing" not in st.session_state:
    st.session_state.processing = False
else:
    # Reset a stuck True flag -- can happen if the browser closes mid-request
    if st.session_state.processing and not st.session_state.get("chat_history"):
        st.session_state.processing = False

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("🎯 CareerFit RAG Coach")
    st.divider()

    # Confirmed-working OpenRouter models.
    OPENROUTER_MODELS = [
        "openai/gpt-4o-mini",
        "google/gemini-2.0-flash-001",
        "anthropic/claude-haiku-4-5",
    ]

    # Ollama Cloud models — accessed directly via ollama.com/v1 (no :cloud suffix needed).
    # Only shown when OLLAMA_BASE_URL points at ollama.com and OLLAMA_API_KEY is set.
    OLLAMA_CLOUD_MODELS = [
        "gpt-oss:120b",
        "gpt-oss:20b",
        "gemma3:27b",
    ]

    _ollama_url = os.getenv("OLLAMA_BASE_URL", "")
    _ollama_key = os.getenv("OLLAMA_API_KEY", "")
    _ollama_is_cloud = "ollama.com" in _ollama_url

    st.markdown("**Model**")
    st.caption("Via OpenRouter. Requires OPENROUTER_API_KEY in .env")
    selected_model = st.selectbox(
        "Model",
        options=OPENROUTER_MODELS,
        index=0,
        label_visibility="collapsed",
        key="cloud_model_select",
    )

    if _ollama_is_cloud and _ollama_key:
        st.divider()
        st.markdown("**Ollama Cloud**")
        st.caption("Billed to your ollama.com account.")
        use_ollama = st.toggle(
            "Switch to Ollama Cloud",
            value=False,
            key="use_ollama_toggle",
        )
        if use_ollama:
            selected_model = st.selectbox(
                "Ollama Cloud model",
                options=OLLAMA_CLOUD_MODELS,
                key="ollama_model_select",
            )

    st.divider()

    st.markdown("**Mode**")
    mode = st.radio(
        "Mode",
        options=[
            "Ask Career Base",
            "Analyze Job Fit",
            "Application Positioning",
            "Interview Prep",
        ],
        label_visibility="collapsed",
        key="mode_radio",
    )

    _MODE_HINTS = {
        "Ask Career Base":         "Ask anything about background or skills.",
        "Analyze Job Fit":         "Paste a JD, get a fit score and honest gaps.",
        "Application Positioning": "Paste a JD, get cover letter points and what to avoid.",
        "Interview Prep":          "Paste a JD, get 10 likely questions with STAR notes.",
    }
    st.caption(_MODE_HINTS[mode])

    _req = st.session_state.get("request_count", 0)
    st.progress(_req / 50, text=f"{_req} / 50 requests used")

    st.divider()

    st.markdown("**Extra tools** *(optional)*")

    enable_company = st.toggle(
        "🔍 Company research",
        value=False,
        help="Searches the web for company info when you name a specific employer. Works in all modes.",
        key="enable_company_toggle",
    )
    if enable_company:
        st.caption("On in all modes. Only triggers when a company name is mentioned.")

    # Job search only available in Ask Career Base mode.
    _jobs_available = mode == "Ask Career Base"
    # disabled=True prevents clicking but does NOT force the session-state value to False.
    # Multiplying by _jobs_available ensures it evaluates to False in other modes.
    enable_jobs = st.toggle(
        "🗂️ Live job search",
        value=False,
        disabled=not _jobs_available,
        help="Finds real job listings via Adzuna. Only works in Ask Career Base mode.",
        key="enable_jobs_toggle",
    ) and _jobs_available
    if not (mode == "Ask Career Base"):
        st.caption("Job search only works in Ask Career Base mode.")
    elif enable_jobs:
        if not (os.getenv("ADZUNA_APP_ID") and os.getenv("ADZUNA_APP_KEY")):
            st.caption("Add ADZUNA_APP_ID and ADZUNA_APP_KEY to `.env` to activate.")
        else:
            st.caption("Active. Try: 'Find me AI content roles in Berlin.'")

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------
_MODE_PROMPTS = {
    "Ask Career Base": "{input}",
    "Analyze Job Fit": "Analyze my fit for this job description and provide a structured fit analysis:\n\n{input}",
    "Application Positioning": "Generate application positioning content for this job description:\n\n{input}",
    "Interview Prep": "Prepare interview questions and STAR-style answer notes for this job description:\n\n{input}",
}

tab_coach, tab_about = st.tabs(["🎯 Coach", "ℹ️ About"])

# ===========================================================================
# TAB 1 -- COACH
# ===========================================================================
with tab_coach:
    hdr_left, hdr_right = st.columns([5, 1])
    with hdr_left:
        st.header(mode)
    with hdr_right:
        st.write("")
        if st.session_state.confirm_clear:
            st.warning("Clear the conversation?")
            c_yes, c_no = st.columns(2)
            if c_yes.button("Yes", use_container_width=True, type="primary", key="confirm_yes"):
                st.session_state.chat_history = []
                st.session_state.thread_id = str(uuid.uuid4())
                st.session_state.agent_memory = MemorySaver()  # wipe agent's turn history
                st.session_state.confirm_clear = False
                st.session_state.processing = False
                st.rerun()
            if c_no.button("No", use_container_width=True, key="confirm_no"):
                st.session_state.confirm_clear = False
                st.rerun()
        elif st.session_state.chat_history:
            if st.button("🗑 Clear", use_container_width=True, key="clear_btn"):
                st.session_state.confirm_clear = True
                st.rerun()

    # -----------------------------------------------------------------------
    # Input form
    # -----------------------------------------------------------------------
    with st.form(key="input_form", clear_on_submit=True):
        if mode == "Ask Career Base":
            user_input = st.text_input(
                "Your question",
                placeholder="e.g. What experience can I point to for a creative AI role?",
            )
        else:
            user_input = st.text_area(
                "Job description",
                height=180,
                placeholder="Paste the full job description here, the more complete the better.",
            )
            char_count = len(user_input) if user_input else 0
            _char_color = "red" if char_count > 14_000 else "grey"
            st.caption(f":{_char_color}[{char_count:,} / 15,000 characters]")

        submitted = st.form_submit_button("Submit", use_container_width=True)

    # -----------------------------------------------------------------------
    # Handle submission
    # -----------------------------------------------------------------------
    if submitted:
        _now = time.time()
        _seconds_since_last = _now - st.session_state.last_submit_time

        if _seconds_since_last < 3.0:
            st.warning(f"Give it {3.0 - _seconds_since_last:.1f}s before submitting again.")
            st.stop()

        if st.session_state.request_count >= 50:
            st.error("You've hit 50 requests for this session. Refresh the page to start fresh.")
            st.stop()

        is_valid, validation_msg = sanitise_input(user_input)

        if not is_valid:
            st.warning(validation_msg)
        else:
            if validation_msg:
                st.warning(validation_msg)

            agent_prompt = _MODE_PROMPTS[mode].format(input=user_input)
            st.session_state.chat_history.append(
                {"role": "user", "content": user_input, "mode": mode, "tools_called": []}
            )
            st.session_state.processing = True

            error_msg = None

            with st.spinner("Searching the knowledge base and writing a response..."):
                try:
                    result = run_agent(
                        user_message=agent_prompt,
                        model_name=selected_model,
                        thread_id=st.session_state.thread_id,
                        enable_company_research=enable_company,
                        enable_job_search=enable_jobs,
                        mode=mode,
                        memory=st.session_state.agent_memory,
                    )
                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": result["response"],
                            "mode": mode,
                            "tools_called": result["tool_calls"],
                            "cost_info": estimate_cost(
                                input_text=user_input,
                                output_text=result["response"],
                                model=selected_model,
                            ),
                            "model": selected_model,
                        }
                    )
                except Exception as exc:
                    st.session_state.chat_history.pop()
                    raw_err = str(exc)
                    _log.error("agent error: %s", raw_err)
                    _err_lower = raw_err.lower()

                    if any(k in _err_lower for k in ("connection error", "connecterror", "connection refused", "failed to connect", "unreachable")):
                        error_msg = (
                            "Connection error reaching OpenRouter. "
                            "Check your internet and `OPENROUTER_API_KEY` in `.env`."
                        )
                    elif any(k in _err_lower for k in ("401", "unauthorized", "authentication", "invalid api key", "forbidden")):
                        error_msg = (
                            "Authentication failed. Check `OPENROUTER_API_KEY` in `.env`, "
                            "it may be expired or wrong."
                        )
                    elif any(k in _err_lower for k in ("429", "rate limit", "too many requests")):
                        error_msg = "Rate limit hit. Wait a few seconds and try again."
                    elif any(k in _err_lower for k in ("model", "not found", "404")):
                        error_msg = (
                            f"Model `{selected_model}` not found. "
                            "Try a different one from the sidebar."
                        )
                    elif any(k in _err_lower for k in ("timeout", "timed out")):
                        error_msg = (
                            "The model took too long to respond. "
                            "Try again or pick a faster model like `gpt-4o-mini`."
                        )
                    else:
                        error_msg = f"Something went wrong: {raw_err}"
                finally:
                    st.session_state.processing = False

            if error_msg:
                st.error(error_msg)
            else:
                st.session_state.last_submit_time = time.time()
                st.session_state.request_count += 1
                st.rerun()

    # -----------------------------------------------------------------------
    # Empty state
    # -----------------------------------------------------------------------
    if not st.session_state.chat_history and not st.session_state.processing:
        st.markdown(
            "<div style='text-align:center; padding: 3rem 0; color: grey;'>"
            "<p style='font-size:2rem;'>🎯</p>"
            "<p style='font-size:1.1rem; font-weight:600;'>Pick a mode and paste a job description to get started.</p>"
            "<p>Or switch to Ask Career Base and ask anything about the background.</p>"
            "</div>",
            unsafe_allow_html=True,
        )

    # -----------------------------------------------------------------------
    # Conversation history -- newest first
    # -----------------------------------------------------------------------
    for msg in reversed(st.session_state.chat_history):
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.caption(f"*{msg['mode']}*")
                content = msg["content"]
                if len(content) > 300:
                    st.markdown(truncate_text(content, max_chars=300))
                    with st.expander("Show full input"):
                        st.markdown(content)
                else:
                    st.markdown(content)
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])

                if msg.get("cost_info"):
                    ci = msg["cost_info"]
                    st.caption(
                        f"~{ci['input_tokens']} in / ~{ci['output_tokens']} out tokens  |  "
                        f"est. ${ci['estimated_cost_usd']:.4f}"
                    )

                with st.expander("Sources, tools & RAG pipeline"):
                    if msg["tools_called"]:
                        st.markdown("**Tools called this turn:**")
                        for t in msg["tools_called"]:
                            st.markdown(f"- `{t}`")
                    else:
                        st.markdown("*No extra tools were called. Response came from the knowledge base only.*")

                    st.divider()
                    st.caption("RAG pipeline for this response")
                    c1, a1, c2, a2, c3, a3, c4, a4, c5 = st.columns(
                        [3, 0.5, 3, 0.5, 3, 0.5, 3, 0.5, 3]
                    )
                    c1.info("📥 Your input")
                    a1.markdown("<p style='text-align:center;padding-top:10px'>→</p>", unsafe_allow_html=True)
                    c2.info("🔄 Query expansion\n(3 to 5 phrases)")
                    a2.markdown("<p style='text-align:center;padding-top:10px'>→</p>", unsafe_allow_html=True)
                    c3.info("🔍 ChromaDB\nvector search")
                    a3.markdown("<p style='text-align:center;padding-top:10px'>→</p>", unsafe_allow_html=True)
                    c4.info("🤖 LLM grounds\nresponse in KB")
                    a4.markdown("<p style='text-align:center;padding-top:10px'>→</p>", unsafe_allow_html=True)
                    c5.info("✅ Cited\nanswer")

    # -----------------------------------------------------------------------
    # Export
    # -----------------------------------------------------------------------
    if st.session_state.chat_history:
        st.divider()

        def _build_markdown_export():
            lines = ["# CareerFit RAG Coach - Conversation Export\n"]
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    lines.append(f"## You ({msg.get('mode', '')})\n\n{msg['content']}\n")
                else:
                    lines.append(f"## Coach\n\n{msg['content']}")
                    if msg.get("tools_called"):
                        lines.append(f"\n*Tools used: {', '.join(msg['tools_called'])}*\n")
                    lines.append("")
            return "\n".join(lines)

        st.download_button(
            label="Export conversation",
            data=_build_markdown_export(),
            file_name="careerfit_conversation.md",
            mime="text/markdown",
            use_container_width=True,
        )

# ===========================================================================
# TAB 2 -- ABOUT
# ===========================================================================
with tab_about:
    st.markdown("## What is this?")

    st.markdown(
        "This tool is built around one person's career profile. "
        "Avishek Chatterjee's CV, case studies, skills inventory, goals, and real application "
        "examples are all in the knowledge base. Every response comes from that material. "
        "It won't pad things out with generic career advice or invent experience that isn't there. "
        "If the evidence doesn't exist in the knowledge base, it says so rather than guessing."
    )
    st.markdown(
        "It's not a general-purpose career tool. "
        "It works for the candidate whose data is in it, and that's intentional."
    )

    st.markdown("---")

    st.markdown("### The four modes")

    st.markdown(
        "**Ask Career Base** is for freeform questions about background, skills, or experience. "
        "It's a good starting point before committing to a full application. "
        "Something like *'What experience do I have that's relevant to an AI education role?'* "
        "works well here."
    )
    st.markdown(
        "**Analyze Job Fit** takes a job description and returns a fit score from 0 to 100, "
        "matched strengths with source citations, honest gaps, and a positioning angle. "
        "Nothing in the gaps section is softened."
    )
    st.markdown(
        "**Application Positioning** takes a job description and returns a cover letter paragraph "
        "ready to adapt, five proof points with citations, and a list of claims to avoid making."
    )
    st.markdown(
        "**Interview Prep** takes a job description and returns ten likely questions "
        "with STAR-format answer notes pulled from the knowledge base."
    )

    st.markdown("---")

    st.markdown("### Choosing a model")

    st.markdown(
        "The sidebar has three OpenRouter models to pick from. "
        "GPT-4o Mini, Gemini 2.0 Flash, and Claude Haiku. "
        "All three need an `OPENROUTER_API_KEY` to work. "
        "GPT-4o Mini is the default and handles all four modes well."
    )
    st.markdown(
        "If `OLLAMA_BASE_URL` points at ollama.com and `OLLAMA_API_KEY` is set in the `.env` file, "
        "an Ollama Cloud toggle appears in the sidebar with three open-source models. "
        "GPT-OSS 120B, GPT-OSS 20B, and Gemma3 27B. "
        "Those run on your Ollama Cloud account and are worth trying for longer, "
        "more considered responses."
    )

    st.markdown("---")

    st.markdown("### Getting the best results")

    st.markdown(
        "Paste the full job description, not just the title. "
        "The retrieval looks at the specific language in the responsibilities and requirements. "
        "A title alone won't surface the right context."
    )
    st.markdown(
        "After each response, open the **Sources, tools and RAG pipeline** section at the bottom "
        "of the reply. It shows which knowledge base files were cited. "
        "If something in the response feels off, that's usually the place to find out why."
    )
    st.markdown(
        "Run Ask Career Base first if you want to check what evidence exists before committing "
        "to a full analysis. It stops you from getting a detailed response built on thin ground."
    )

    st.markdown("---")

    st.markdown("### Something not working?")

    st.markdown(
        "If the input is under 20 characters, the tool won't run. Paste more text.\n\n"
        "If the job description is over 15,000 characters, trim it. "
        "Legal boilerplate at the bottom of the posting is usually where the extra length comes from.\n\n"
        "If you get an authentication error, `OPENROUTER_API_KEY` isn't set. "
        "Running locally, add it to the `.env` file. "
        "On Streamlit Cloud, add it under Settings then Secrets in your app dashboard.\n\n"
        "If a model returns an error, switch to a different one in the sidebar. "
        "Some OpenRouter models go offline from time to time.\n\n"
        "If the Ollama Cloud toggle isn't showing up, check that `OLLAMA_BASE_URL` is set to "
        "`https://ollama.com/v1/` and that `OLLAMA_API_KEY` contains a valid ollama.com key."
    )

    st.markdown("---")

    st.caption(
        "Built by Avishek Chatterjee as part of the Turing College AI Engineering programme."
    )
