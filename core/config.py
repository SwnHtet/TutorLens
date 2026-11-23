"""Central settings for TutorLens.

Change the values here, or override the three model settings in the .env file.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

# ---- folders -------------------------------------------------------------
DATA_DIR = ROOT / "data"
PDF_DIR = DATA_DIR / "pdfs"
CHROMA_DIR = DATA_DIR / "chroma"
DB_PATH = DATA_DIR / "tutorlens.db"
PROMPT_DIR = ROOT / "prompts"

for _folder in (DATA_DIR, PDF_DIR, CHROMA_DIR):
    _folder.mkdir(parents=True, exist_ok=True)

# ---- models (set these in .env) ------------------------------------------
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "").strip()
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").strip()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3").strip()

# ---- chunking and retrieval ----------------------------------------------
CHUNK_MAX_CHARS = 1200       # target size of one chunk
CHUNK_OVERLAP_CHARS = 150    # a short last paragraph is repeated in the next chunk
TOP_K = 4                    # how many chunks to retrieve for a question
MIN_SIMILARITY = 0.35        # below this, we say "not in this PDF" (tune it!)
SECTION_CONTEXT_CHARS = 6000 # max text sent to the LLM when explaining a section

# ---- LLM behaviour -------------------------------------------------------
TEMP_TEACH = 0.4             # a little creativity for explanations
TEMP_JSON = 0.0             # low temperature = consistent questions and marks
LLM_TIMEOUT_SECONDS = 300    # local models can be slow on a laptop


def load_prompt(name: str) -> str:
    """Read prompts/<name>.md as text."""
    return (PROMPT_DIR / f"{name}.md").read_text(encoding="utf-8")


def render_prompt(name: str, **values: object) -> str:
    """Fill {placeholders} in a prompt file in a single pass.

    Single pass means text inside the values (for example the PDF text) is
    never treated as a placeholder itself.
    """
    template = load_prompt(name)
    return re.sub(
        r"\{(\w+)\}",
        lambda match: str(values.get(match.group(1), match.group(0))),
        template,
    )