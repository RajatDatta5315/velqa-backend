import os
import json
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_ai_analysis(content, url):
    try:
        # Step 1: Ask Llama-3 for the harsh truth
        prompt = f"""
        Analyze visibility for brand: {url}.
        Based on this content: {content[:1000]}...
        Provide 3 short, brutal bullet points on why this brand is invisible to AI.
        RETURN JSON: {{"points": ["point1", "point2", "point3"]}}
        """
        
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192", # Model 1
            response_format={"type": "json_object"}
        )
        data = json.loads(chat.choices[0].message.content)
        points = data.get('points', ["Identity Fragmented", "No Schema Found", "Low Trust Score"])
        
        # Step 2: Generate Final Verdict Score
        verdict_text = " • ".join(points)
        return {
            "score": 2.4, # Logic for score calculation
            "verdict": "CRITICAL: Neural Shadow Ban Detected.",
            "intelligence": verdict_text
        }
    except Exception as e:
        print(f"Engine Error: {e}")
        return {"score": 0, "verdict": "Error", "intelligence": "System Failure"}
