import os
from openai import OpenAI

# Initialize OpenAI client with provided environment variables
client = OpenAI(
    api_key=os.environ.get("API_KEY"),
    base_url=os.environ.get("API_BASE_URL")
)

def llm_priority(obs):
    """Use LLM to assign priority instead of rules"""
    text = f"Title: {obs.get('title', '')}\nDescription: {obs.get('description', '')}"
    
    response = client.chat.completions.create(
        model="gpt-4",  # or whatever model is available
        messages=[
            {
                "role": "system",
                "content": "You are a code review prioritizer. Respond with only a single number: 0 (low), 1 (medium), or 2 (high)."
            },
            {
                "role": "user",
                "content": f"What priority should this PR have?\n\n{text}"
            }
        ],
        temperature=0.7
    )
    
    try:
        priority = int(response.choices[0].message.content.strip())
        return max(0, min(2, priority))  # Clamp to 0-2
    except:
        return 1  # Default to medium if parsing fails
