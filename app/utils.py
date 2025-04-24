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
    "As a task assignment reviewer, evaluate an extension request. "
    "A talent needs more time due to the following reason: "
    f"\"{reason}\". "
    f"Another talent is {'available' if is_other_talent_available else 'not available'} to take over.\n\n"
    "The extension should be approved if the reason provided is valid, regardless of whether another talent is available. "
    "Respond with only 'yes' if the reason is valid, and 'no' otherwise.")

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