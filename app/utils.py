import random
import os
from google import genai
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from the parent directory
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Retrieve the API key from environment variables
api_key = os.getenv("GOOGLE_API_KEY")

# Configure the GenAI client with the API key
client = genai.Client(api_key=api_key)

def get_fake_embedding():
    return [random.random() for _ in range(512)]

def serialize_embedding(embedding):
    return ",".join(map(str, embedding))

def deserialize_embedding(string):
    return list(map(float, string.split(",")))

def should_approve_extension(reason: str, is_other_talent_available: bool) -> bool:
    """
    Determines whether to approve an extension request based on the provided reason
    and the availability of other talent.

    Args:
        reason (str): The reason for the extension request.
        is_other_talent_available (bool): Indicates if other talent is available.

    Returns:
        bool: True if the extension should be approved, False otherwise.
    """
    prompt = (
    "You are a task assignment reviewer. A talent has requested an extension for the following reason:\n\n"
    f"\"{reason}\"\n\n"
    f"Is another talent available to take over the task? {is_other_talent_available}.\n\n"
    f"Based on the validity of the reason and the availability of other talent, should we approve the extension request? Approve the request only if the reason is valid, even if another talent is available. Respond with only 'yes' or 'no'."
)

    try:
        # Generate a response from the model
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        answer = response.text.strip().lower()
        return "yes" in answer
    except Exception as e:
        # Handle exceptions (e.g., API errors)
        print(f"Error during Gemini API call: {e}")
        return False