import requests
from bs4 import BeautifulSoup
import os
from groq import Groq

# Groq Client setup
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def scrape_site(url):
    try:
        if not url.startswith('http'): url = 'https://' + url
        res = requests.get(url, timeout=7, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.content, 'html.parser')
        return soup.get_text(separator=' ', strip=True)[:3000]
    except Exception as e:
        print(f"Scrape Error: {e}")
        return None

def get_ai_analysis(content):
    try:
        prompt = f"Analyze this business content for AI Search Visibility (GEO). Give a score out of 10 and a short verdict on how AI models see this brand. Return ONLY JSON with keys 'score' and 'verdict': {content}"
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        return chat.choices[0].message.content
    except Exception as e:
        print(f"AI Error: {e}")
        return '{"score": 0, "verdict": "Neural Link Timeout. Try again."}'
