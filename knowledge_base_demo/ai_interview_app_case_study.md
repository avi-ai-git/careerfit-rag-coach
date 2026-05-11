## Quick Reference -- Key Facts for Retrieval

- Live URL: https://ai-interview-practice-app-made-by-avi-ai.streamlit.app/
- External code review: Vytautas Bunevičius, Nord Security
- Security finding: no rate limiting = API credits burnout risk via prompt injection
- Stack: Python, Streamlit, Anthropic Claude API (claude-sonnet), RAG
- 5 prompt engineering techniques implemented
- Turing College Sprint 1 project
- Learning-in-public: security finding posted on LinkedIn, not hidden

---

# Case Study: AI Interview Practice App
*Turing College LLM Application Development — Sprint 1*

## What It Is

A live, publicly accessible Streamlit application that helps job seekers prepare for interviews. Users provide a job description and their background. The app generates tailored interview questions, evaluates practice answers in real time, and provides structured feedback — all grounded in the user's actual experience via RAG.

**Live at:** https://ai-interview-practice-app-made-by-avi-ai.streamlit.app/

---

## The Problem It Solves

Generic AI chatbots give generic interview prep. "Tell me about a time you showed leadership" is the same answer regardless of whether you're applying for a junior PM role or a creative director position. This app uses the user's specific background and the specific job description to generate questions that are actually relevant — and evaluates answers against what that particular role actually requires.

---

## Technical Architecture

**Stack:**
- Backend: Python
- UI: Streamlit
- LLM: Anthropic Claude API (claude-sonnet model)
- Key pattern: Retrieval-Augmented Generation (RAG) — user's CV and job description are chunked and retrieved to ground question generation in the user's actual experience

**5 Prompt Engineering Techniques Implemented:**
1. Role-definition system prompt — establishes the LLM as an experienced interviewer for the specific role
2. Output format constraints — forces structured JSON with question text, competency being assessed, and ideal answer framework
3. Few-shot examples — provides 2-3 sample Q&A pairs to calibrate tone and depth
4. Retrieval grounding — every question generation prompt includes retrieved CV passages so questions reference the candidate's actual background
5. Self-consistency evaluation — answer feedback prompt independently rates the answer on multiple rubric dimensions before synthesizing a score

**Key architecture decisions:**
- RAG over fine-tuning: for variable-input documents (different CVs and JDs each session), RAG is faster to implement, requires no training data, and adapts without retraining
- Claude over GPT-4: longer context window handles full CV plus JD in a single pass; strong instruction-following for structured JSON output
- Semantic chunking: CV sections chunked by role and achievement unit rather than fixed token count, to preserve meaning during retrieval

---

## External Code Review

The app was code-reviewed by **Vytautas Bunevičius (Security Engineer, Nord Security)**.

**Finding:** No rate limiting on API calls. This creates a prompt injection risk where a malicious user could craft inputs to trigger large numbers of API calls, burning through API credits rapidly.

**Response:** Rather than quietly patching the issue, Demo Candidate posted the finding publicly on LinkedIn as part of an honest learning-in-public approach. The post documented what was found, why it matters, and what the fix involves. This is consistent with the project's design principle: honest self-assessment of production readiness is more valuable than presenting a polished-but-fragile facade.

---

## Honest Gaps Acknowledged

- This is a learning project, not production-ready code. Error handling is basic.
- No persistent database — state resets between sessions.
- Embedding and vector store is a lightweight local implementation, not a production vector DB (e.g., Pinecone, Weaviate).
- No authentication or multi-user support.
- Rate limiting gap identified by external reviewer (documented above).

These gaps are acknowledged because understanding them is evidence of engineering judgment — knowing what you built, what it can handle, and what it cannot.

---

## What This Project Demonstrates

- Practical LLM application development: end-to-end from idea to live deployed app
- RAG architecture: document chunking, embedding, vector retrieval applied to a real use case
- Prompt engineering: 5 distinct techniques implemented and documented
- External review process: willingness to have work examined by a real security professional
- Honest self-assessment: production readiness gaps documented, not hidden
- Learning in public: security finding shared on LinkedIn, not buried

**Relevant for:** AI Deployment roles, Developer Advocate, AI Educator, Creative Technologist with technical component, any role where "can you actually ship things" is the question.
