import json
import os
from google import genai

# 1. قراءة ملف البيانات الموحد
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 2. استدعاء الـ SDK الرسمي لـ Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

cv_types = ['flutter', 'backend', 'fullstack']

for cv_type in cv_types:
    print(f"Generating optimized text for {cv_type} CV...")
    
    prompt = f"""
    You are an expert ATS-optimized CV writer. Generate a professional CV in clean Markdown format based on this user data: {json.dumps(data)}.
    Target Role for this CV: {cv_type} developer.
    
    Strict Instructions:
    1. Filter the projects to highlight mostly {cv_type} relevant skills and achievements.
    2. Rewrite project descriptions using strong action verbs and include industry keywords for ATS.
    3. Output ONLY the raw markdown content without any chat or wrapper like ```markdown.
    """
    
    # استخدام الموديل المستقر والسريع عبر المكتبة الرسمية
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    
    markdown_content = response.text
    
    # حفظ الملفات الناتجة
    os.makedirs('cvs', os.path.ok=True)
    md_file_path = f'cvs/{cv_type}_cv.md'
    with open(md_file_path, 'w', encoding='utf-8') as out_file:
        out_file.write(markdown_content)

print("CV Text generated successfully via Official SDK!")
