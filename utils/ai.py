import os
import requests
import json
from loguru import logger
from typing import Optional, Dict, Any

# Default model
DEFAULT_MODEL = "xiaomi/mimo-v2-flash:free" 

def get_openrouter_api_key() -> Optional[str]:
    """Retrieves the OpenRouter API key from environment variables."""
    return os.getenv("OPENROUTER_API_KEY")

def generate_project_brief(project_data: Dict[str, Any], model: str = DEFAULT_MODEL) -> Optional[str]:
    """
    Generates a project brief using OpenRouter.
    
    Args:
        project_data: A dictionary containing project details (title, description, etc.)
        model: The OpenRouter model ID to use.
        
    Returns:
        The generated text or None if the request failed.
    """
    api_key = get_openrouter_api_key()
    if not api_key:
        logger.error("OPENROUTER_API_KEY not found in environment variables.")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:8501", # Required by OpenRouter, using local default
        "X-Title": "HopOn Project Matcher", # Optional
        "Content-Type": "application/json"
    }

    # Construct a prompt from the project data
    title = project_data.get('title', 'Unknown Project')
    description = project_data.get('description', '')
    objective = project_data.get('objective', '')
    
    # Combine description and objective if both exist, or use whichever is available
    full_text = f"{description}\n\n{objective}".strip()
    
    # Secure Prompt Construction using XML delimiters
    prompt = f"""
    You are an expert technical analyst. Create a concise "One-Pager" project brief based ONLY on the data provided in the <project_data> block below.
    
    <project_data>
    Title: {title}
    
    Description/Objective:
    {full_text}
    </project_data>
    
    Please provide the output in the following Markdown format: 
    
    ## 📝 Summary
    (2-3 sentences explaining what the project does)
    
    ## 🛠️ Key Technologies & Methods
    * (List of inferred technologies, methodologies, or scientific domains)
    
    ## 🚀 Potential Impact
    (Brief assessment of the market or scientific impact)
    """

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload),
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        else:
            logger.error(f"Unexpected response format from OpenRouter.")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"OpenRouter API request failed: {e}")
        return None
