import os
import requests
import json

def get_recipe_recommendations(ingredients: list) -> list:
    api_key = os.getenv('GROQ_API_KEY')
    
    ingredients_text = ", ".join([
        f"{i['name']} ({i['quantity']} {i['unit']})" for i in ingredients
    ])

    prompt = f"""Kamu adalah asisten memasak Indonesia. Berdasarkan bahan-bahan berikut:
{ingredients_text}

Berikan LEBIH DARI 3 rekomendasi resep masakan Indonesia.
Prioritaskan bahan yang hampir kedaluwarsa.

Balas HANYA dengan JSON array berikut (tanpa teks lain, tanpa markdown):
[
  {{
    "recipe_name": "Nama Resep",
    "ingredients_used": "Bahan1 (100g), Bahan2 (200g), Bahan3 (50g)",
    "instructions": "Langkah 1: ... Langkah 2: ... Langkah 3: ...",
    "nutrition_estimate": "Kalori: ~300 kkal, Protein: ~15g, Karbohidrat: ~30g, Lemak: ~10g",
    "servings": 3,
    "servings_description": "Cukup untuk 3 porsi (masing-masing ~200g)",
    "leftover_potential": "Biasanya ada sisa 1-2 porsi jika dimasak untuk 2 orang",
    "price_estimate": 15000
  }}
]"""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000,
                "temperature": 0.7,
            },
            timeout=30,
        )
        
        print("Status:", response.status_code)
        print("Response:", response.text[:500])
        
        content = response.json()['choices'][0]['message']['content']
        
        content = content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        recipes = json.loads(content)
        return recipes
    
    except Exception as e:
        print(f"Groq API Error: {e}")
        import traceback
        traceback.print_exc()
        return []