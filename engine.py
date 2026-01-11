def get_ai_analysis(content, url):
    # Ensemble Logic
    # Complex Analysis -> Llama-3-70b
    # Fast Verification -> Mixtral-8x7b
    
    prompt = f"Analyze {url} based on {content}. Provide a 3-point brutal neural audit. Be sophisticated, not generic."
    
    # Call Groq with llama3-70b-8192
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
