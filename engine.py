import requests
from bs4 import BeautifulSoup
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def scrape_site(url):
    try:
        if not url.startswith('http'): url = 'https://' + url
        res = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.content, 'html.parser')
        return soup.get_text()[:2000]
    except: return None

def get_ai_analysis(content):
    prompt = f"Analyze site for AI Visibility: {content}. Return ONLY JSON with keys: 'ai_recognition', 'score', 'verdict'."
    chat = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
        response_format={"type": "json_object"}
    )
    return chat.choices[0].message.content
