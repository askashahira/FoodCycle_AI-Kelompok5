import os
import requests
import json

def get_recipe_recommendations(ingredients: list) -> list:
    api_key = os.getenv('GROQ_API_KEY')
    
    ingredients_text = ", ".join([
        f"{i['name']} ({i['quantity']} {i['unit']})" for i in ingredients
    ])

    prompt = f"""Kamu adalah asisten memasak. Berdasarkan bahan-bahan berikut:
{ingredients_text}

Berikan TEPAT 3 rekomendasi resep masakan Indonesia yang bisa dibuat.
Prioritaskan menggunakan semua atau sebagian besar bahan yang ada.

Balas HANYA dengan JSON array berikut (tanpa teks lain, tanpa markdown):
[
  {{
    "recipe_name": "Nama Resep",
    "ingredients_used": "Bahan1, Bahan2, Bahan3",
    "instructions": "Langkah 1: ... Langkah 2: ... Langkah 3: ...",
    "nutrition_estimate": "Kalori: ~300 kkal, Protein: ~15g, Karbohidrat: ~30g, Lemak: ~10g",
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