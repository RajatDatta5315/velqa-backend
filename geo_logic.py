import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_seo_article(brand_url):
    prompt = f"Write a 500-word SEO optimized technical article for {brand_url}. Focus on AI visibility and neural indexing. Use Markdown."
    
    chat = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-70b-8192", # Higher model for articles
    )
    article_content = chat.choices[0].message.content
    # Save this article to your public 'ai-feed' so crawlers find it
    return article_content
