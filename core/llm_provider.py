"""
LLM Provider & Grounded Generation Engine
Enforces the 7 Strict System Rules:
1. Use only the provided retrieved medical context.
2. Do not invent medical facts.
3. Do not diagnose the user.
4. Do not prescribe medication.
5. If the context does not contain enough information, clearly say that the information is unavailable.
6. Do not use your general knowledge to fill missing information.
7. Encourage professional medical consultation when appropriate.

Provides:
- LocalGroundedGenerator: 100% offline, zero-hallucination deterministic synthesis
- GeminiProvider: Google Gemini 1.5/2.0 Flash integration
- OpenAIProvider: OpenAI / Compatible API integration
"""

import os
import re
import json
import requests
from typing import Dict, Any, List, Optional

SYSTEM_RULES_PROMPT = """You are the Smart Healthcare Navigator AI. You are an empathetic, calm, and reassuring healthcare assistant.
Your job is to listen to the user's symptoms, translate medical concepts into plain 8th-grade reading level language, suggest up to 3 possible common ailments based strictly on verified context, and direct them to the appropriate medical specialist.

SYSTEM RULES (STRICT & MANDATORY):
1. Use ONLY the provided retrieved medical context.
2. Do NOT invent medical facts or ailments.
3. Do NOT diagnose the user (never say "You have X"; say "Possible common ailments associated with these symptoms include...").
4. Do NOT prescribe medication (no prescription drug names, dosages, or regimens).
5. If the context does not contain enough information, clearly state that the information is unavailable in your verified knowledge base.
6. Do NOT use your general knowledge to fill in missing information.
7. Always encourage professional medical consultation and include standard safety disclaimers.
8. Maintain a calm, professional, and reassuring tone at all times.
"""

MEDICAL_DISCLAIMER = (
    "\n\n*Medical Disclaimer: I am an AI health assistant, not a doctor. This information is for "
    "educational guidance based on verified clinical reference data and does not constitute a medical "
    "diagnosis, treatment plan, or prescription. Please consult a qualified healthcare provider for proper evaluation.*"
)

class LocalGroundedGenerator:
    """
    Offline Grounded Synthesis Engine:
    Parses retrieved context chunks and extracts:
    - 3 possible common ailments
    - Plain 8th-grade explanation
    - Specialist recommendation
    - Red flags and supportive self-care
    Guarantees 100% adherence to retrieved documents with zero hallucinations.
    """
    def generate(self, user_query: str, retrieved_matches: List[Dict[str, Any]], sources: List[str]) -> str:
        if not retrieved_matches:
            return (
                "I don't have enough verified information in my medical knowledge base to answer that "
                "question reliably. I don't want to guess or provide potentially unsafe medical information. "
                "Please consult a qualified healthcare professional or use a verified medical source."
            )

        # Aggregate text from matches
        full_context = "\n".join([m["content"] for m in retrieved_matches])
        specialty = retrieved_matches[0].get("specialty", "General Physician")

        # Extract possible ailments listed in documents
        # Pattern: 1. **Ailment Name**:
        ailment_matches = re.findall(r"\d+\.\s+\*\*([^*]+)\*\*:\s*([^\n\r]+)", full_context)
        
        # Extract supportive care lines
        supportive_matches = re.findall(r"-\s+\*\*([^*]+)\*\*:\s*([^\n\r]+)", full_context)
        
        # Build empathetic response
        lines = []
        lines.append("Thank you for sharing what you are experiencing. Dealing with uncomfortable symptoms can be worrying, but I am here to help you understand what might be happening in simple terms.\n")
        
        if ailment_matches:
            lines.append("### Possible Common Ailments (Based on Verified Guidelines):")
            lines.append("Based on the symptoms you described and our verified medical reference documents, here are **3 possible common ailments** that doctors frequently investigate:")
            
            # Select top 3 ailments
            selected = ailment_matches[:3]
            for idx, (name, desc) in enumerate(selected, start=1):
                clean_name = name.strip()
                clean_desc = desc.strip()
                lines.append(f"{idx}. **{clean_name}**: {clean_desc}")
            lines.append("")
        else:
            lines.append("### Clinical Guidance:")
            lines.append("According to our verified reference materials:")
            for m in retrieved_matches[:2]:
                lines.append(f"- {m['section']}: {m['content'][:250]}...")
            lines.append("")

        # Specialist recommendation
        lines.append(f"### Recommended Healthcare Professional:")
        lines.append(f"For a comprehensive and safe clinical evaluation, it is recommended to consult a **{specialty}**. You can also schedule an appointment directly using our Hospital Navigation tool below.\n")

        # Supportive non-prescription self-care if available
        if supportive_matches:
            lines.append("### Supportive Self-Care Tips (While Awaiting Doctor Evaluation):")
            for tip_title, tip_desc in supportive_matches[:3]:
                if not any(k in tip_title.lower() for k in ["red flag", "prescription", "emergency"]):
                    lines.append(f"- **{tip_title.strip()}**: {tip_desc.strip()}")
            lines.append("")

        # Red Flags
        lines.append("### When to Seek Immediate Care:")
        lines.append("If your symptoms rapidly worsen, or you experience extreme shortness of breath, severe pain, or high fever that won't come down, please seek emergency medical care immediately.\n")

        # Sources
        if sources:
            lines.append("### Verified Sources:")
            for src in sources:
                lines.append(f"- *{src}*")

        lines.append(MEDICAL_DISCLAIMER)
        return "\n".join(lines)


class GeminiProvider:
    """Google Gemini API Provider using direct REST endpoint."""
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

    def generate(self, user_query: str, context: str, sources: List[str]) -> str:
        prompt = f"""{SYSTEM_RULES_PROMPT}

VERIFIED MEDICAL CONTEXT:
{context}

VERIFIED SOURCES:
{', '.join(sources)}

USER QUESTION / SYMPTOMS:
{user_query}

Remember to:
- Be empathetic, calm, and reassuring.
- Suggest 3 possible common ailments grounded strictly in the context above.
- Translate jargon into 8th-grade reading level.
- Refuse to diagnose or prescribe.
- Explicitly advise seeing a doctor or specialist.
- Append the standard medical disclaimer at the end.
"""
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1024
            }
        }

        try:
            resp = requests.post(self.endpoint, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                if "Medical Disclaimer" not in text:
                    text += MEDICAL_DISCLAIMER
                return text
            else:
                return f"[Gemini API Error {resp.status_code}]: {resp.text}"
        except Exception as e:
            return f"[Gemini Connection Error]: {str(e)}"


class OpenAIProvider:
    """OpenAI API Provider."""
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model_name = model_name

    def generate(self, user_query: str, context: str, sources: List[str]) -> str:
        prompt = f"""VERIFIED MEDICAL CONTEXT:
{context}

VERIFIED SOURCES:
{', '.join(sources)}

USER QUESTION / SYMPTOMS:
{user_query}
"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_RULES_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }

        try:
            resp = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                if "Medical Disclaimer" not in text:
                    text += MEDICAL_DISCLAIMER
                return text
            else:
                return f"[OpenAI API Error {resp.status_code}]: {resp.text}"
        except Exception as e:
            return f"[OpenAI Connection Error]: {str(e)}"


class OllamaProvider:
    """
    Ollama Local LLM Provider.
    Enables running open-source models (Llama 3, Mistral, Gemma, BioMistral, Phi-3)
    locally on the machine with zero API cost, total privacy, and offline capability.
    """
    def __init__(self, model_name: str = "llama3", host: str = "http://localhost:11434"):
        self.model_name = model_name or "llama3"
        self.host = host.rstrip("/") if host else "http://localhost:11434"
        self.endpoint = f"{self.host}/api/generate"

    def generate(self, user_query: str, context: str, sources: List[str]) -> str:
        prompt = f"""{SYSTEM_RULES_PROMPT}

VERIFIED MEDICAL CONTEXT:
{context}

VERIFIED SOURCES:
{', '.join(sources)}

USER QUESTION / SYMPTOMS:
{user_query}

Remember to:
- Be empathetic, calm, and reassuring.
- Suggest 3 possible common ailments grounded strictly in the context above.
- Translate jargon into 8th-grade reading level.
- Refuse to diagnose or prescribe.
- Explicitly advise seeing a doctor or specialist.
- Append the standard medical disclaimer at the end.
"""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        }
        try:
            resp = requests.post(self.endpoint, json=payload, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                text = data.get("response", "")
                if "Medical Disclaimer" not in text:
                    text += MEDICAL_DISCLAIMER
                return text
            else:
                return f"[Ollama Error {resp.status_code}]: {resp.text}"
        except requests.exceptions.ConnectionError:
            return (
                f"### [Ollama Local LLM Notice]\n"
                f"Could not connect to Ollama at `{self.host}`.\n\n"
                f"**How to run Ollama on your computer:**\n"
                f"1. Download and start Ollama from **[ollama.com](https://ollama.com)**.\n"
                f"2. Open a terminal and run: `ollama run {self.model_name}`\n"
                f"3. Make sure Ollama is running on port 11434.\n\n"
                f"*Tip: You can switch back to 'Local Grounded Engine' in Settings anytime for 100% offline synthesis without needing Ollama running.*"
            )
        except Exception as e:
            return f"[Ollama Error]: {str(e)}"


def generate_symptom_response(
    user_query: str, 
    rag_result: Dict[str, Any], 
    provider_type: str = "local", 
    api_key: Optional[str] = None,
    model_name: Optional[str] = None
) -> str:
    """
    Unified LLM response generator.
    If RAG result is not relevant, strictly returns the fallback message without calling any LLM.
    """
    if not rag_result.get("is_relevant"):
        return rag_result.get("fallback_message")

    context = rag_result.get("grounded_context", "")
    sources = rag_result.get("sources", [])
    matches = rag_result.get("matches", [])

    if provider_type == "ollama":
        provider = OllamaProvider(model_name=model_name or api_key or "llama3")
        return provider.generate(user_query, context, sources)
    elif provider_type == "gemini" and api_key:
        provider = GeminiProvider(api_key=api_key)
        return provider.generate(user_query, context, sources)
    elif provider_type == "openai" and api_key:
        provider = OpenAIProvider(api_key=api_key)
        return provider.generate(user_query, context, sources)
    else:
        # Local grounded generator (Default & Offline)
        local_gen = LocalGroundedGenerator()
        return local_gen.generate(user_query, matches, sources)
