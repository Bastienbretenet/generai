import json
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

def load_prompt(filename: str, **kwargs) -> str:
    template = (PROMPTS_DIR / filename).read_text(encoding="utf-8")
    return template.format(**kwargs)

def prompt_extract_relevant_tables(schema: dict, user_request: str) -> str:
    return load_prompt(
        "extract_relevant_tables.txt",
        schema=json.dumps(schema, indent=2, ensure_ascii=False),
        user_request=user_request,
    )

def prompt_generate_fixtures(filtered_schema: dict, user_request: str, project_context: str = "", protected_data: dict | None = None) -> str:
    protected_section = ""
    if protected_data:
        protected_section = json.dumps(protected_data, indent=2, ensure_ascii=False, default=str)
    return load_prompt(
        "generate_fixtures.txt",
        schema=json.dumps(filtered_schema, indent=2, ensure_ascii=False),
        user_request=user_request,
        project_context=project_context,
        protected_data=protected_section,
    )

def prompt_fix_fixtures(user_request: str, sql: str, error: str, project_context: str = "") -> str:
    return load_prompt(
        "fix_fixtures.txt",
        user_request=user_request,
        sql=sql,
        error=error,
        project_context=project_context,
    )
