---
doc_id: example_job_descriptions
doc_type: test_inputs
visibility: demo
purpose: Stable synthetic job descriptions for testing CareerFit RAG Coach job-fit analysis, retrieval, gap detection, and application positioning.
source_note: These are paraphrased/synthetic test job descriptions inspired by public job postings and role descriptions. They are not copied job ads and should be replaced with real target job descriptions during active applications.
---

# Example Job Descriptions — CareerFit RAG Coach Test Inputs

## How to Use This File

Use these job descriptions as stable test cases for CareerFit RAG Coach.

They are intentionally varied:
- some are strong fits,
- some are medium/stretch fits,
- some are weak fits,
- some are adjacent but not ideal.

This helps test whether the app can do more than produce generic positive feedback. A good RAG job-fit assistant should identify both evidence-backed strengths and honest gaps.

Recommended test modes:
1. Paste one JD into **Analyze Job Fit**.
2. Compare the fit score against the expected fit level.
3. Check whether the app retrieves the right source files.
4. Run **Application Positioning**.
5. Run **Interview Prep**.
6. Check whether unsupported claims are avoided.

---

## Public Role Inspiration Sources

These synthetic examples were inspired by public role descriptions and market patterns, including:
- GenAI Creative Technologist roles emphasizing repeatable GenAI workflows for high-quality marketing assets at scale.
- AI Content Strategist roles emphasizing AI trends, content workflows, responsible AI guidelines, and internal enablement.
- AI Instructional Designer roles combining instructional design, digital content production, program delivery, and AI adoption.
- AI Developer Advocate / Developer Relations roles emphasizing educational technical content, developer community engagement, product feedback, tutorials, and examples.
- AI Deployment / AI Strategist roles emphasizing enablement, adoption, customer training, technical depth, and measurable business value.
- AI Marketing Operations roles emphasizing AI-powered workflows, campaign personalization, integrations, and performance tuning.

---

# JD 1 — AI Content Strategist / GenAI Enablement Manager

## Expected Fit Level

High

## Why This Is a Good Test

This should retrieve:
- `hike_case_study.md`
- `skills_inventory.md`
- `cv_summary.md`
- `career_goals.md`

It should identify strong evidence in AI tool adoption, prompt library design, content strategy, and internal enablement.

## Job Description

We are looking for an AI Content Strategist to help our marketing and content teams use generative AI responsibly and effectively. The role sits between content strategy, marketing operations, and internal enablement.

You will design AI-assisted content workflows, create prompt libraries, define guidelines for responsible AI use, and train non-technical teams on practical GenAI use cases. You will also work with marketing, brand, and product stakeholders to improve campaign speed, consistency, and quality.

### Responsibilities

- Build and maintain prompt libraries for content, research, ideation, and campaign production.
- Train marketing and communications teams on practical AI workflows.
- Translate fast-moving AI tool changes into usable playbooks and templates.
- Support content strategy across LinkedIn, website, newsletters, campaign pages, and thought leadership.
- Create responsible AI usage guidelines, including copyright, quality control, and human review principles.
- Partner with non-technical stakeholders to identify repeatable AI use cases.
- Measure workflow improvements, adoption, and content output quality.

### Requirements

- 3+ years in content strategy, marketing, communications, or enablement.
- Hands-on experience with generative AI tools such as ChatGPT, Claude, Gemini, Midjourney, Perplexity, or similar.
- Strong writing and editing ability.
- Experience creating workshops, playbooks, templates, or internal training materials.
- Ability to explain AI tools clearly to non-technical teams.
- Comfort working in a fast-changing environment.

### Nice to Have

- Experience with Notion or similar knowledge management systems.
- Experience producing social, video, or campaign content.
- Experience with AI governance, content quality control, or responsible AI frameworks.

---

# JD 2 — GenAI Creative Technologist

## Expected Fit Level

High / Medium-High

## Why This Is a Good Test

This should retrieve:
- `hike_case_study.md`
- `skills_inventory.md`
- `cv_summary.md`
- possibly `career_goals.md`

It should identify strong creative AI production and workflow design, while checking whether the role demands deeper frontend/prototyping skills.

## Job Description

We are hiring a GenAI Creative Technologist to help our creative and marketing teams build scalable, high-quality AI-assisted production workflows.

This role is not about casually experimenting with AI tools. It is about turning generative AI into repeatable creative systems that improve speed, quality, consistency, and brand control across campaigns.

### Responsibilities

- Design and test GenAI workflows for image, video, copy, and campaign asset production.
- Build repeatable production pipelines using tools such as Midjourney, Runway, Firefly, DALL·E, ElevenLabs, ComfyUI, or similar.
- Partner with designers, copywriters, marketers, and strategists to turn creative concepts into AI-assisted production systems.
- Document workflows, prompts, quality-control steps, and brand consistency rules.
- Prototype new ways of scaling creative output while keeping human review and creative direction in the loop.
- Educate internal teams on what current AI tools can and cannot do.

### Requirements

- Portfolio showing creative technology, AI-assisted content, interactive media, video, motion, campaign systems, or digital experiments.
- Strong understanding of generative AI image/video/audio tools.
- Ability to communicate with creative and technical teams.
- Strong visual judgment and quality-control instincts.
- Experience documenting workflows and turning experiments into reusable systems.

### Nice to Have

- Frontend prototyping experience.
- Experience with node-based creative tools or automation workflows.
- Experience in agency, brand, or studio environments.
- Understanding of legal, brand, and ethical risks in AI-generated creative work.

---

# JD 3 — AI Instructional Designer / Digital Learning Specialist

## Expected Fit Level

High

## Why This Is a Good Test

This should retrieve:
- `giz_case_study.md`
- `hike_case_study.md`
- `education.md`
- `skills_inventory.md`

It should emphasize curriculum design, bootcamp delivery, LMS redesign, onboarding, learning experience design, and AI adoption.

## Job Description

We are looking for an AI-focused Instructional Designer to design learning experiences, workshops, and digital training materials for professionals adopting generative AI tools.

You will work with subject matter experts to convert complex AI topics into practical learning experiences for non-technical audiences. You will also help improve digital learning assets and use AI tools to accelerate production and iteration.

### Responsibilities

- Design workshops, bootcamps, self-paced modules, and digital learning materials.
- Translate AI concepts into practical exercises for non-technical learners.
- Build templates, exercises, prompts, and facilitation guides.
- Use AI tools to draft, improve, and personalize learning content.
- Support program delivery, learner onboarding, and post-session feedback loops.
- Improve LMS content structure, onboarding journeys, and learner engagement.
- Work with stakeholders to define learning goals and success metrics.

### Requirements

- Experience designing workshops, training programs, or educational content.
- Understanding of generative AI tools and prompt engineering.
- Strong writing, facilitation, and stakeholder communication skills.
- Experience with digital learning platforms, LMS systems, or knowledge bases.
- Ability to simplify technical topics without oversimplifying risks and limitations.

### Nice to Have

- Experience with startup, innovation, or professional education environments.
- Experience measuring learning engagement or program outcomes.
- Experience creating video, social, or multimedia learning content.

---

# JD 4 — Developer Advocate, AI Platform

## Expected Fit Level

Medium / Stretch

## Why This Is a Good Test

This should retrieve:
- `sprint1_project.md`
- `skills_inventory.md`
- `hike_case_study.md`
- `education.md`
- `career_goals.md`

The app should recognize strong communication, education, community, and AI learning evidence, but also identify gaps in professional software engineering depth, sample code, SDK expertise, and developer community credibility.

## Job Description

We are looking for an AI Developer Advocate to help developers understand, build with, and give feedback on our AI platform.

You will create technical education content, tutorials, demos, videos, documentation, and example applications. You will speak with developers, gather product feedback, and help product and engineering teams understand where users struggle.

### Responsibilities

- Create tutorials, videos, blog posts, code examples, and demo applications.
- Explain AI platform concepts clearly to developer and semi-technical audiences.
- Build lightweight example apps using APIs, SDKs, and frameworks.
- Engage with developer communities online and at events.
- Collect feedback from users and translate it into product insights.
- Collaborate with product, engineering, marketing, and documentation teams.
- Support launches with educational content and community-facing messaging.

### Requirements

- Strong communication and teaching ability.
- Hands-on experience building with AI APIs or LLM tools.
- Ability to write technical tutorials and explain code.
- Familiarity with Python or JavaScript.
- Comfort speaking publicly or leading workshops.
- Understanding of RAG, agents, prompt engineering, or evaluation.

### Nice to Have

- Experience as a software engineer, solutions engineer, or developer advocate.
- Portfolio of technical writing, demos, GitHub projects, or videos.
- Experience with OpenAI, Anthropic, LangChain, vector databases, or similar tools.

---

# JD 5 — AI Marketing Operations Manager

## Expected Fit Level

Medium-High / Stretch

## Why This Is a Good Test

This should retrieve:
- `skills_inventory.md`
- `hike_case_study.md`
- `cv_summary.md`
- `career_goals.md`

The app should find marketing + AI workflow strengths, but it should also identify gaps around technical integrations, CRM/marketing automation systems, and production marketing ops tooling.

## Job Description

We are hiring an AI Marketing Operations Manager to identify, test, and scale AI workflows across the marketing team.

The role combines marketing operations, AI experimentation, process design, prompt engineering, campaign support, and cross-functional enablement. You will help marketers move from ad hoc AI use to repeatable workflows that improve speed, personalization, and quality.

### Responsibilities

- Identify high-value AI use cases across content, lifecycle marketing, SDR workflows, campaign planning, and reporting.
- Prototype prompt workflows, lightweight agents, or AI-assisted templates.
- Support marketing teams in testing AI tools and evaluating output quality.
- Work with operations and data teams to connect AI workflows with existing marketing systems.
- Document playbooks, governance principles, and quality-control processes.
- Train marketers on responsible and repeatable AI usage.
- Measure adoption, time saved, quality improvement, or workflow impact.

### Requirements

- Experience in marketing, marketing operations, content strategy, or growth.
- Strong hands-on experience with generative AI tools.
- Ability to translate team pain points into AI-enabled workflows.
- Strong documentation and internal enablement skills.
- Comfort working with cross-functional teams.

### Nice to Have

- Experience with CRM, marketing automation, or analytics tools.
- Basic API or automation knowledge.
- Experience with Langdock, Zapier, n8n, HubSpot, Salesforce, or similar tools.
- Experience implementing AI workflows beyond individual prompting.

---

# JD 6 — AI Deployment Manager / Customer Enablement

## Expected Fit Level

Medium / Stretch

## Why This Is a Good Test

This should retrieve:
- `sprint1_project.md`
- `skills_inventory.md`
- `education.md`
- `cv_summary.md`
- `career_goals.md`

The app should identify fit in enablement, training, communication, adoption, and AI education, but also flag gaps around enterprise AI deployments, technical implementation, APIs, security, and customer-facing solution design.

## Job Description

We are looking for an AI Deployment Manager to help enterprise customers adopt AI products successfully. This is a post-sales enablement role focused on training, implementation support, use-case development, and measurable adoption.

You will work with customer teams to identify workflows, design enablement programs, support adoption, and communicate product value. You should be comfortable discussing AI capabilities and limitations with both business and technical stakeholders.

### Responsibilities

- Lead onboarding and enablement programs for enterprise AI customers.
- Help customers identify high-impact AI use cases.
- Design repeatable adoption playbooks and training materials.
- Support workshops, office hours, and stakeholder sessions.
- Translate technical AI product capabilities into business value.
- Partner with sales, product, engineering, and customer success teams.
- Measure usage, adoption, activation, and business outcomes.

### Requirements

- Experience in enablement, customer success, solution consulting, technical training, or AI education.
- Strong communication skills with business and technical stakeholders.
- Hands-on experience with generative AI tools and workflows.
- Ability to design training materials and adoption frameworks.
- Comfort discussing LLMs, agents, APIs, or AI product limitations.

### Nice to Have

- Experience with ChatGPT Enterprise, Claude Enterprise, LangChain, RAG, Codex, or AI agents.
- Experience implementing AI systems in enterprise workflows.
- Technical background in Python, APIs, data, or software delivery.
- Experience in SaaS customer success or solution engineering.

---

# JD 7 — AI Engineer / RAG Application Developer

## Expected Fit Level

Low / Technical Stretch

## Why This Is a Good Test

This should retrieve:
- `sprint1_project.md`
- `education.md`
- `skills_inventory.md`

The app should not overrate this. It should acknowledge developing technical skills but clearly flag missing professional engineering depth, backend experience, testing, deployment, cloud, and production RAG experience.

## Job Description

We are looking for an AI Engineer to build and maintain production-grade LLM applications using RAG, agents, vector databases, and backend APIs.

You will design and implement retrieval pipelines, evaluate model performance, write production Python services, integrate external tools, and deploy AI applications to cloud infrastructure.

### Responsibilities

- Build backend services for LLM-powered applications.
- Implement RAG pipelines with document ingestion, chunking, embeddings, vector retrieval, reranking, and evaluation.
- Integrate LLM APIs, tools, and agents into user-facing products.
- Write tests, monitor latency and cost, and improve reliability.
- Deploy services using Docker and cloud infrastructure.
- Collaborate with product and engineering teams on architecture decisions.

### Requirements

- 3+ years professional Python or backend engineering experience.
- Experience with LangChain, LlamaIndex, or custom RAG pipelines.
- Experience with vector databases such as Pinecone, Weaviate, Chroma, or FAISS.
- Experience deploying software to cloud platforms.
- Strong software engineering practices, testing, logging, monitoring, and CI/CD.
- Ability to debug production systems.

### Nice to Have

- Experience with agent frameworks, MCP, RAGAS, LangSmith, or observability tools.
- Experience with fine-tuning, evaluation datasets, or model selection.
- Experience with enterprise data security.

---

# JD 8 — Traditional Communications Manager

## Expected Fit Level

Medium

## Why This Is a Good Test

This should retrieve:
- `cv_summary.md`
- `hike_case_study.md`
- `giz_case_study.md`
- `skills_inventory.md`

The app should identify communications strengths, but also note that this role may underuse the candidate's AI specialization unless the organization is innovation-focused.

## Job Description

We are looking for a Communications Manager to support internal and external communications across campaigns, stakeholder updates, website copy, social media, and executive messaging.

This is a general communications role with limited AI focus. The ideal candidate can write clearly, manage stakeholders, coordinate campaigns, and produce communication materials across formats.

### Responsibilities

- Plan and execute communication campaigns.
- Write copy for website, newsletters, LinkedIn, press materials, and internal updates.
- Coordinate with teams across departments to collect information and align messaging.
- Support video, visual, and event communication needs.
- Maintain editorial calendars and ensure consistent tone of voice.
- Track basic engagement metrics and adjust content accordingly.

### Requirements

- 3+ years communications, marketing, or content experience.
- Strong writing and editing skills.
- Stakeholder management experience.
- Experience with social media, newsletters, and campaign planning.
- Ability to turn complex information into clear messages.

### Nice to Have

- Experience in public sector, education, culture, or technology organizations.
- Experience with multimedia production.
- Experience using AI tools for content workflows.

---

# JD 9 — Community Manager at AI-Native Company

## Expected Fit Level

Medium-High

## Why This Is a Good Test

This should retrieve:
- `hike_case_study.md`
- `skills_inventory.md`
- `cv_summary.md`
- `career_goals.md`

The app should connect community education, startup/founder ecosystem, content, workshops, and AI tool enthusiasm. It should also identify whether community moderation, SaaS community operations, or formal DevRel experience is missing.

## Job Description

We are hiring a Community Manager for an AI-native software company. You will help grow and support a community of builders, marketers, creators, and operators using our AI product.

This role combines content, events, education, user feedback, and community operations. You should be comfortable explaining AI features, running online sessions, writing useful content, and identifying user stories.

### Responsibilities

- Grow and engage an online community around an AI product.
- Host workshops, AMAs, onboarding sessions, and product education events.
- Create helpful content such as guides, templates, prompts, videos, and newsletters.
- Collect feedback from users and share insights with product and marketing teams.
- Identify community champions and customer stories.
- Support launches, campaigns, and educational programming.

### Requirements

- Experience in community, content, education, marketing, or startup ecosystem work.
- Strong understanding of generative AI tools.
- Excellent writing and facilitation skills.
- Ability to create practical resources for non-technical users.
- Comfort working across product, marketing, and customer-facing teams.

### Nice to Have

- Experience with Discord, Slack, LinkedIn, newsletters, or community platforms.
- Experience in SaaS, startup, or AI-native company environments.
- Experience with developer or creator communities.

---

# JD 10 — Senior Backend / MLOps Engineer

## Expected Fit Level

Low

## Why This Is a Good Test

This is a negative-control test case. The app should clearly say this is not a good fit based on the current KB.

It should retrieve:
- `skills_inventory.md`
- `career_goals.md`
- maybe `sprint1_project.md`

It should explicitly avoid recommending the candidate for deep backend, MLOps, production cloud, and infrastructure-heavy roles.

## Job Description

We are looking for a Senior Backend / MLOps Engineer to design, deploy, and maintain scalable machine learning infrastructure.

You will build APIs, deploy model-serving systems, manage cloud infrastructure, monitor production systems, and work closely with ML researchers and data engineers.

### Responsibilities

- Design and maintain backend services for ML products.
- Build model-serving infrastructure.
- Implement CI/CD pipelines for ML systems.
- Deploy services to Kubernetes and cloud environments.
- Monitor latency, reliability, cost, and model performance.
- Maintain data pipelines and observability systems.
- Collaborate with ML scientists on production deployment.

### Requirements

- 5+ years backend engineering experience.
- Strong Python, FastAPI, Docker, Kubernetes, and cloud infrastructure experience.
- Experience with MLOps tools and model-serving patterns.
- Experience with CI/CD, monitoring, logging, and incident response.
- Strong software architecture and production operations experience.

### Nice to Have

- Experience with MLflow, Kubeflow, Airflow, Ray, or similar.
- Experience with GPU infrastructure.
- Experience with regulated enterprise environments.

---

# Suggested Evaluation Questions Based on These JDs

Use these later in `evaluation/test_questions.json`.

1. Which source files support a strong fit for AI Content Strategist?
2. Which evidence supports GenAI Creative Technologist roles?
3. What are the strongest proof points for AI Instructional Designer roles?
4. Where are the gaps for AI Developer Advocate roles?
5. Is AI Marketing Operations Manager a strong fit or a stretch?
6. What evidence supports AI Deployment Manager, and what gaps remain?
7. Why is AI Engineer / RAG Developer a technical stretch?
8. Is a traditional Communications Manager role a good strategic target?
9. What evidence supports Community Manager at an AI-native company?
10. Why is Senior Backend / MLOps Engineer not a good fit?

