import re

def clean_email_text(text):
    """Remove quoted text, signatures, and excessive whitespace from email bodies."""
    # Remove quoted replies (simple heuristic)
    text = re.sub(r'On .+ wrote:\n.+', '', text, flags=re.DOTALL)
    # Remove common signature delimiters
    text = re.sub(r'--\s*\n.*', '', text, flags=re.DOTALL)
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def prepare_prompt(email_text, context=None, language='en', tone='professional'):
    prompt = f"""
You are an AI assistant for business email communication.
Language: {language}
Tone: {tone}
Context: {context or 'N/A'}

Email:
{email_text}
"""
    return prompt

def postprocess_ai_response(response_text):
    """Clean and format AI response for display or sending."""
    # Remove leading/trailing whitespace and fix common formatting issues
    return response_text.strip() 