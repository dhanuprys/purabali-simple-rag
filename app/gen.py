import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
GENERATIVE_MODEL = "gemini-2.5-flash"

def generate_response(user_query: str, retrieved: list[dict]) -> str:
    system_instruction = (
        "Anda adalah seorang ahli di bidang pariwisata Bali. "
        "Anda akan membantu pengunjung untuk mengetahui informasi tentang tempat wisata di Bali. "
        "Anda akan memberikan informasi tentang tempat wisata di Bali yang relevan dengan pertanyaan pengunjung. "
        "Informasi yang Anda berikan harus sesuai dengan fakta yang ada di dalam database. "
        "Jangan memberikan informasi yang tidak sesuai dengan fakta yang ada di dalam database. "
        "Gunakan kalimat yang sopan dan profesional."
        "Berikut ini merupakan database tempat wisata di Bali: \n"
    )
    docs = "\n".join(
        f"- [{r['meta']['type']}] {r['meta']['nama']}: {r['text']}"
        for r in retrieved
    )
    user_section = f"\n\nPertanyaan: {user_query}\nJawaban:"
    prompt = system_instruction + docs + user_section
    config = types.GenerateContentConfig(
        temperature=0.2,
        top_p=0.9,
        max_output_tokens=512,
    )
    resp = client.models.generate_content(
        model=GENERATIVE_MODEL,
        contents=prompt,
        config=config
    )
    return resp.text.strip() if resp.text else ""
