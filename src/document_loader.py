from pathlib import Path
from langchain_core.documents import Document

_DOC_TYPE_MAP = {
    "cv_summary.md": "cv_summary",
    "skills_inventory.md": "skills_inventory",
    "career_goals.md": "career_goals",
    "career_principles.md": "career_principles",
    "education.md": "education",
    "hike_case_study.md": "case_study",
    "giz_case_study.md": "case_study",
    "ai_interview_app_case_study.md": "case_study",
    "ctrl_alt_deity_case_study.md": "case_study",
    "farout_case_study.md": "case_study",
    "application_examples.md": "application_examples",
}


def infer_doc_type(filename: str) -> str:
    return _DOC_TYPE_MAP.get(filename, "markdown")


def load_documents(knowledge_base_dir) -> list:
    kb_path = Path(knowledge_base_dir).resolve()
    documents = []
    for md_file in sorted(kb_path.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        metadata = {
            "source": md_file.name,
            "path": str(md_file),
            "doc_type": infer_doc_type(md_file.name),
        }
        documents.append(Document(page_content=content, metadata=metadata))
    return documents
