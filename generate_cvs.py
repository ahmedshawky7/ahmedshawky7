
import json
import os
from pathlib import Path
from google import genai

# 1. Load unified CV data
with open("data.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# 2. Check Gemini API Key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing!")

# 3. Initialize Gemini client
client = genai.Client(api_key=api_key)

# 4. CV types
cv_types = ["flutter", "backend", "fullstack"]

# 5. Create output directory
output_dir = Path("cvs")
output_dir.mkdir(parents=True, exist_ok=True)

# 6. Generate each CV
for cv_type in cv_types:

    print(f"\nGenerating {cv_type} CV...")

    prompt = f"""
You are an expert ATS-optimized CV writer.

Generate a professional CV in clean Markdown format
based on the following user data:

{json.dumps(data, ensure_ascii=False, indent=2)}

Target Role:
{cv_type} Developer

Strict Instructions:

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

5. Rewrite descriptions using strong action verbs.

6. Optimize keywords for ATS systems.

7. Keep the CV professional, concise, and suitable
   for junior developer positions.

8. Do not invent experience, achievements, or skills.

9. Do not invent URLs. Use only the provided links.
   Omit invalid or placeholder links.

10. Output ONLY raw Markdown.
    Do not include ```markdown or any explanation.

"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        markdown_content = response.text

        if not markdown_content:
            raise ValueError(
                f"Gemini returned empty content for {cv_type}"
            )

        # Remove accidental Markdown code fences
        markdown_content = markdown_content.strip()

        if markdown_content.startswith("```markdown"):
            markdown_content = markdown_content[len("```markdown"):]

        elif markdown_content.startswith("```"):
            markdown_content = markdown_content[3:]

        if markdown_content.endswith("```"):
            markdown_content = markdown_content[:-3]

        markdown_content = markdown_content.strip()

        # Save generated Markdown
        md_file_path = output_dir / f"{cv_type}_cv.md"

        md_file_path.write_text(
            markdown_content,
            encoding="utf-8"
        )

        print(f"Successfully generated: {md_file_path}")

    except Exception as error:
        print(f"Failed to generate {cv_type} CV: {error}")
        raise

print("\nAll CVs generated successfully!")
