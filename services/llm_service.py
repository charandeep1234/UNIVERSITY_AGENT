"""
Generative AI and RAG Response Service
Connects to Google Gemini API (via google-genai or google-generativeai)
with high-quality Fallback RAG synthesizer if offline or key is missing.
"""
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PROMPT_TEMPLATE = """You are a helpful Smart University Academic Assistant.

Answer the student's question using only the information provided in the university knowledge base.

Retrieved Context:
{context}

Student Question:
{question}

Provide a clear, concise, accurate, and student-friendly answer.
Do not invent information.
If the answer is not available in the provided context, clearly state that the information is not available in the university knowledge base."""

def _synthesize_fallback_response(question: str, context: str, source_doc: str, category: str) -> str:
    """
    Intelligent Rule-Based RAG Synthesizer that generates clean, student-friendly
    grounded responses directly from the retrieved document context without needing an external API.
    """
    if not context or "No sufficiently relevant document" in context:
        return (
            "Sorry, I could not find relevant information in the university knowledge base.\n\n"
            "Please try asking your question differently or add relevant information to the Knowledge Base."
        )
        
    # Clean up the context text
    cleaned_lines = [line.strip() for line in context.splitlines() if line.strip()]
    
    # Filter out pure headers if redundant
    filtered_lines = [l for l in cleaned_lines if not l.isupper() or len(l.split()) > 4]
    if not filtered_lines:
        filtered_lines = cleaned_lines
        
    body_text = "\n\n".join(filtered_lines[:4])
    
    # Construct professional student-friendly response
    doc_display = source_doc.replace(".txt", "").replace("_", " ").title()
    
    response = (
        f"Based on the official university **{doc_display}** ({source_doc}):\n\n"
        f"{body_text}\n\n"
        f"*(Note: Information retrieved directly from the verified university knowledge base.)*"
    )
    return response

def generate_ai_response(question: str, context: str, source_doc: str, category: str = "General") -> dict:
    """
    Generate the final student response using RAG.
    Attempts Google Gemini API first; gracefully falls back if key is missing or call fails.
    
    Args:
        question (str): The student's question.
        context (str): The retrieved knowledge base text chunk(s).
        source_doc (str): Name of the retrieved document.
        category (str): Query category.
        
    Returns:
        dict: {
            "response": str,
            "is_fallback": bool,
            "model_name": str,
            "status": str
        }
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    
    # If no API key or placeholder key, use Fallback RAG immediately
    if not api_key or api_key == "your_api_key_here" or api_key == "your_gemini_api_key_here":
        fallback_text = _synthesize_fallback_response(question, context, source_doc, category)
        return {
            "response": fallback_text,
            "is_fallback": True,
            "model_name": "RAG Knowledge Synthesizer (Offline/Fallback Mode)",
            "status": "Generated via local RAG context synthesizer (No Gemini API key provided)"
        }
        
    # Attempt Google Gemini API
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)
    
    try:
        # Try new google-genai SDK
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        if response and response.text:
            return {
                "response": response.text.strip(),
                "is_fallback": False,
                "model_name": "Google Gemini 2.5 Flash",
                "status": "Generated via Google Gemini API"
            }
    except Exception as e_genai:
        print(f"[LLMService] google-genai attempt failed: {e_genai}. Trying alternative...")
        
    try:
        # Try legacy google.generativeai if installed
        import google.generativeai as legacy_genai
        legacy_genai.configure(api_key=api_key)
        model = legacy_genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        if response and response.text:
            return {
                "response": response.text.strip(),
                "is_fallback": False,
                "model_name": "Google Gemini 1.5 Flash",
                "status": "Generated via Google Gemini API"
            }
    except Exception as e_legacy:
        print(f"[LLMService] Legacy Gemini attempt failed: {e_legacy}")

    # Seamless Fallback when API call fails
    print("[LLMService] Gemini API unreachable or failed. Engaging Smart RAG fallback synthesizer.")
    fallback_text = _synthesize_fallback_response(question, context, source_doc, category)
    return {
        "response": fallback_text,
        "is_fallback": True,
        "model_name": "RAG Knowledge Synthesizer (API Fallback)",
        "status": "Generated via local RAG fallback synthesizer (API offline/rate-limited)"
    }
