import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_seo_article(brand_url):
    # Using 8b for better speed and stability
    prompt = f"Act as a Senior SEO Journalist. Write a high-authority news article about {brand_url} joining the Generative AI Index. Focus on its neural reputation and brand authority. Use professional tone. Markdown format."
    
    try:
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192", 
        )
        return chat.choices[0].message.content
    except:
        return "Article generation pending... Neural nodes busy."
