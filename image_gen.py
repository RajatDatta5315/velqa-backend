from PIL import Image, ImageDraw, ImageFont
import os

def generate_brand_card(brand_url, score):
    # Create a dark minimalist background (Apple style)
    img = Image.new('RGB', (800, 400), color='#000000')
    d = ImageDraw.Draw(img)
    
    # Border
    d.rectangle([20, 20, 780, 380], outline="#1a1a1a", width=2)
    
    # Text (Fonts should be on server, fallback to default)
    try:
        font_large = ImageFont.truetype("Inter-Bold.ttf", 60)
        font_small = ImageFont.truetype("Inter-Regular.ttf", 30)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    d.text((50, 50), "VELQA NEURAL INDEX", fill="#555", font=font_small)
    d.text((50, 100), f"Entity: {brand_url}", fill="#fff", font=font_large)
    d.text((50, 250), f"Score: {score}/10", fill="#00ff00" if float(score) > 7 else "#ff4444", font=font_large)
    
    card_path = f"cards/{brand_url}.png"
    if not os.path.exists('cards'): os.makedirs('cards')
    img.save(card_path)
    return card_path
