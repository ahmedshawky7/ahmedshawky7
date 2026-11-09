
import json
import os
import time
import random

from pathlib import Path
from google import genai


# =====================================================
# 1. Load CV Data
# =====================================================

DATA_FILE = Path("data.json")
OUTPUT_DIR = Path("cvs")

if not DATA_FILE.exists():
    raise FileNotFoundError("data.json was not found!")

with DATA_FILE.open("r", encoding="utf-8") as file:
    data = json.load(file)


# =====================================================
# 2. Initialize Gemini Client
# =====================================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing!")

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.8-flash"


# =====================================================
# 3. Create Output Directory
# =====================================================

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =====================================================
# 4. Generate Content With Retry
# =====================================================

def generate_with_retry(prompt, max_attempts=5):

    retryable_errors = [429, 500, 502, 503, 504]

    for attempt in range(1, max_attempts + 1):

        try:
            print(f"Gemini request attempt {attempt}/{max_attempts}")

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )

            if not response.text:
                raise ValueError("Gemini returned empty content!")

            return response

        except Exception as error:

            status_code = getattr(error, "code", None)

            if status_code not in retryable_errors:
                raise

            if attempt == max_attempts:
                print("Maximum retry attempts reached!")
                raise

            wait_time = min(10 * (2 ** (attempt - 1)), 60)
            wait_time += random.uniform(0, 3)

            print(
                f"Gemini temporarily unavailable "
                f"(HTTP {status_code})."
            )

            print(
                f"Retrying in {wait_time:.1f} seconds..."
            )

            time.sleep(wait_time)


# =====================================================
# 5. Clean Markdown Response
# =====================================================

def clean_markdown(content):

    content = content.strip()

    if content.startswith("```markdown"):
        content = content[len("```markdown"):]

    elif content.startswith("```"):
        content = content[3:]

    if content.endswith("```"):
        content = content[:-3]

    return content.strip()


# =====================================================
# 6. Generate CV Prompt
# =====================================================

def build_prompt(cv_type):

    return f"""
You are an expert ATS-optimized CV writer.

Generate a professional CV in clean Markdown format
based on the following user data:

{json.dumps(data, ensure_ascii=False, indent=2)}

Target Role:
{cv_type} Developer

STRICT INSTRUCTIONS:

1. Filter projects to highlight mostly {cv_type}-relevant
   skills, technologies, and achievements.

2. For Flutter CV:
   Focus on Flutter, Dart, Firebase, mobile development,
   Clean Architecture, and mobile projects.

3. For Backend CV:
   Focus on Java, Spring Boot, Spring Security, JWT,
   REST APIs, databases, and backend projects.

4. For Fullstack CV:
   Include relevant mobile, backend, and full-stack
   projects and technologies.

5. Rewrite project descriptions using strong action verbs.

6. Optimize keywords for ATS systems.

7. Keep the CV professional, concise, and suitable
   for junior developer positions.

8. Do not invent experience, achievements, or skills.

9. Do not invent URLs. Use only the provided links.
   Omit invalid or placeholder links.

10. Keep contact information accurate.

11. Output ONLY raw Markdown.
    Do not include code fences or explanations.
"""


# =====================================================
# 7. Generate All CVs
# =====================================================

cv_types = ["flutter", "backend", "fullstack"]

successful_cvs = []
failed_cvs = []

for cv_type in cv_types:

    print("\n" + "=" * 50)
    print(f"Generating {cv_type.upper()} CV...")
    print("=" * 50)

    try:

        prompt = build_prompt(cv_type)

        response = generate_with_retry(prompt)

        markdown_content = clean_markdown(response.text)

        if not markdown_content:
            raise ValueError("Generated Markdown is empty!")

        md_file_path = OUTPUT_DIR / f"{cv_type}_cv.md"

        md_file_path.write_text(
            markdown_content,
            encoding="utf-8"
        )

        successful_cvs.append(cv_type)

        print(f"Successfully generated: {md_file_path}")

    except Exception as error:

        failed_cvs.append(cv_type)

        print(f"Failed to generate {cv_type} CV: {error}")

        # Continue generating the remaining CVs
        continue


# =====================================================
# 8. Final Report
# =====================================================

print("\n" + "=" * 50)
print("CV GENERATION SUMMARY")
print("=" * 50)

print(f"Successful CVs: {len(successful_cvs)}")
print(f"Failed CVs: {len(failed_cvs)}")

if successful_cvs:
    print("\nSuccessfully generated:")

    for cv in successful_cvs:
        print(f"  - {cv}_cv.md")

if failed_cvs:
    print("\nFailed CVs:")

    for cv in failed_cvs:
        print(f"  - {cv}_cv.md")

if failed_cvs:
    raise RuntimeError(
        "Some CVs failed to generate. "
        "Check the logs and rerun the workflow."
    )

print("\nAll CVs generated successfully!")
