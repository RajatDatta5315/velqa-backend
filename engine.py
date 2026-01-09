import requests
from bs4 import BeautifulSoup
import os
import json
from groq import Groq

# Initialize Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def scrape_site(url):
    """Website content fetch karne ke liye"""
    try:
        if not url.startswith('http'): url = 'https://' + url
        res = requests.get(url, timeout=7, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36'})
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, 'html.parser')
            # Removing scripts and styles for cleaner text
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text(separator=' ', strip=True)
            return text[:3000]
        return None
    except Exception as e:
        print(f"Scrape Error: {e}")
        return None

def get_ai_analysis(content):
    """GEO Analysis logic"""
    try:
        prompt = (
            "You are a GEO (Generative Engine Optimization) expert. "
            "Analyze the following website content and determine its visibility to AI models like ChatGPT/Gemini. "
            "Return ONLY a JSON object with keys 'score' (0-10) and 'verdict' (max 20 words). "
            f"Content: {content}"
        )
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        return chat.choices[0].message.content
    except Exception as e:
        print(f"AI Error: {e}")
        return json.dumps({"score": 2, "verdict": "Neural Link Fragmented. High hallucination risk."})

def vigilis_reputation_check(brand_name):
    """Paid users ke liye AI Hallucination monitoring"""
    try:
        # Check how AI perceives the brand reputation
        prompt = f"Does the AI community consider the brand '{brand_name}' as a verified authority or a hallucination risk? Return JSON: {{'threat_level': 'Low/High', 'details': '...'}}"
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        return json.loads(chat.choices[0].message.content)
    except:
        return {"threat_level": "Unknown", "details": "Monitoring active."}
