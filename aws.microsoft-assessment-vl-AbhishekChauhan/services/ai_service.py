import config

def generate_rag_response(prompt: str, context: str, source_citation: str = None) -> str:
    if config.USE_MOCK or not config.GEMINI_API_KEY:
        response = f"[MOCK INSIGHT]: Analysis based on retrieved data:\n{context}"
        if source_citation:
            response += f"\n\nSource: {source_citation}"
        return response

    try:
        from google import genai
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        
        full_prompt = f"Context:\n{context}\n\nUser Question: {prompt}\n\nProvide a concise, professional answer."
        if source_citation:
            full_prompt += f" Explicitly cite the source document '{source_citation}' at the end."
            
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=full_prompt,
        )
        return response.text
    except Exception as e:
        return f"[GEMINI ERROR]: {str(e)}\n\nContext Data: {context}"