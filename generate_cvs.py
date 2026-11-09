import json
import os
import requests

# 1. قراءة ملف البيانات الموحد
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# استخدام موديل gemini-2.5-flash السريع والممتاز
API_URL = f"https://googleapis.com{GEMINI_API_KEY}"

def ask_ai(prompt):
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()['candidates'][0]['content']['parts'][0]['text']

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
    
    markdown_content = ask_ai(prompt)
    
    # تحويل الـ Markdown إلى HTML بسيط ثم إلى PDF
    os.makedirs('cvs', exist_ok=True)
    md_file_path = f'cvs/{cv_type}_cv.md'
    with open(md_file_path, 'w', encoding='utf-8') as out_file:
        out_file.write(markdown_content)

print("CV Text generated. Converting to PDF...")
# سنترك مهمة التحويل للـ GitHub Action باستخدام أداة سريعة
