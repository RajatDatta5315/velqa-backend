from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

def generate_brand_card(brand_url, score, intelligence_text):
    # 1. Canvas Setup (1200x630 for Social Media)
    W, H = 1200, 630
    img = Image.new('RGB', (W, H), color='#050505') # Ultra Dark Grey
    d = ImageDraw.Draw(img)
    
    # 2. Fonts (Load default if custom not found)
    try:
        font_header = ImageFont.truetype("arial.ttf", 60)
        font_score = ImageFont.truetype("arial.ttf", 100)
        font_text = ImageFont.truetype("arial.ttf", 40)
    except:
        font_header = ImageFont.load_default()
        font_score = ImageFont.load_default()
        font_text = ImageFont.load_default()

    # 3. Draw Elements
    # Brand Name
    d.text((50, 50), f"VELQA NEURAL AUDIT: {brand_url.upper()}", fill="#555", font=font_header)
    
    # The Score (Big & Bold)
    color = "#ff4444" if float(score) < 5 else "#00ff00"
    d.text((50, 150), f"{score}/10", fill=color, font=font_score)
    d.text((350, 180), "VISIBILITY SCORE", fill="#fff", font=font_header)

    # 4. The "Fear" Text (Wrapped)
    # Intelligence text ko '•' se tod kar lines banayenge
    lines = intelligence_text.split('•')
    y_text = 300
    for line in lines:
        wrapper = textwrap.TextWrapper(width=50)
        word_list = wrapper.wrap(text=line.strip())
        for element in word_list:
            d.text((50, y_text), f"> {element}", fill="#ccc", font=font_text)
            y_text += 50
        y_text += 20 # Extra gap between points

    # Save
    if not os.path.exists('cards'): os.makedirs('cards')
    card_path = f"cards/{brand_url.replace('.', '_')}.png"
    img.save(card_path)
    return card_path
