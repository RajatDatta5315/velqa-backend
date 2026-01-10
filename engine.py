import requests
from bs4 import BeautifulSoup
import os
import json
from groq import Groq

# Initialize Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def scrape_site(url):
    """Scrapes content while handling blocks for big domains"""
    try:
        if not url.startswith('http'): url = 'https://' + url
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        res = requests.get(url, timeout=10, headers=headers)
        if res.status_code == 200:
            soup = BeautifulSoup(res.content, 'html.parser')
            # Clean up the noise
            for s in soup(["script", "style", "nav", "footer"]):
                s.extract()
            text = soup.get_text(separator=' ', strip=True)
            return text[:4000] # Increased limit for more depth
        return "BLOCKED_OR_UNREACHABLE"
    except Exception as e:
        print(f"Scraping Error: {e}")
        return "ERROR"

def get_ai_analysis(content, url):
    """Generates the 'Aukat' (Detailed AI Intelligence)"""
    try:
        # Prompt to evaluate brand authority even if scraping fails
        prompt = f"""
        ACT AS A NEURAL ARCHITECT. Evaluate the digital entity: {url}.
        CONTENT_DATA: {content}
        
        TASK:
        1. If it's a globally recognized brand (Google, Amazon, etc.), give an 8.5+ score regardless of content blocks.
        2. Generate 'score' (0-10).
        3. Generate 'verdict' (One punchy sentence).
        4. Generate 'intelligence' (A 50-word deep research report on how AI models like GPT-4, Claude, and Gemini perceive this brand. Mention hallucinations, trust nodes, and semantic gaps).
        
        RETURN ONLY JSON:
        {{
            "score": float,
            "verdict": "string",
            "intelligence": "string"
        }}
        """
        
        chat = client.chat.completions.create(
            messages=[{{"role": "user", "content": prompt}}],
            model="llama3-8b-8192",
            response_format={{"type": "json_object"}}
        )
        return chat.choices[0].message.content
    except Exception as e:
        print(f"AI Logic Error: {e}")
        return json.dumps({
            "score": 1.2,
            "verdict": "Neural Sync Failed.",
            "intelligence": "Critical gap in brand indexing. AI models are unable to verify this entity's existence."
        })
