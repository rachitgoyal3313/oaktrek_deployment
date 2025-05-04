import requests
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def generate_ai_response(name, email, message, order_details=""):
    """
    Generate an AI response using OpenRouter.ai
    """
    try:
        # Prepare full context message
        context = f"""
        Customer name: {name}
        Customer email: {email}
        Customer message: {message}

        Order details:
        {order_details}

        Please generate a helpful, professional response to this customer inquiry.
        """

        # Choose a good conversational model (you can experiment)
        model = "mistralai/mistral-7b-instruct"  # or try "openchat/openchat-3.5"

        # Call OpenRouter
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                # "HTTP-Referer": "https://your-domain.com",  # Optional, helps track usage
                # "X-Title": "OakTrek-AI-CustomerSupport",     # Optional, custom project name
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are Rachit.ai,  a helpful and professional customer support assistant for a shoe brand named OakTrek."},
                    {"role": "user", "content": context}
                ]
            },
            timeout=15
        )

        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return generate_fallback_response(name, message)

    except Exception as e:
        logger.exception(f"Error generating AI response: {str(e)}")
        return generate_fallback_response(name, message)

def generate_fallback_response(name, message):
    return f"""
Thank you for contacting OakTrek. We've received your message and our team is reviewing it. 
Someone will get back to you with a more detailed response shortly.

Best regards,  
The OakTrek Team
"""