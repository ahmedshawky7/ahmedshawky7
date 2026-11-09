from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "data.json"
TEMPLATE_DIR = ROOT / "templates"
OUTPUT_DIR = ROOT / "output"

def tex_escape(value: object) -> str:
    """Escape ordinary text before inserting it into LaTeX."""
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)

def safe_url(value: object) -> str:
    url = str(value).strip()
    parsed = urlparse(url)
    if parsed.scheme not in {"https", "http", "mailto"}:
        raise ValueError(f"Unsupported or missing URL scheme: {url}")
    if any(char in url for char in "{}\\\n\r"):
        raise ValueError(f"Unsafe character in URL: {url}")
    return url

def main() -> None:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=False,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["tex"] = tex_escape
    env.filters["url"] = safe_url

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    profiles = data["profiles"]
    for profile_name in ("flutter", "backend", "fullstack"):
        template = env.get_template(f"{profile_name}_cv.tex.j2")
        rendered = template.render(
            personal=data["personal"],
            education=data["education"],
            experience=data["experience"],
            languages=data["languages"],
            profile=profiles[profile_name],
            include_portfolio=(profile_name != "backend"),
        )
        destination = OUTPUT_DIR / f"Ahmed_Shawky_{profile_name.title()}_CV.tex"
        destination.write_text(rendered, encoding="utf-8")
        print(f"Generated: {destination.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
