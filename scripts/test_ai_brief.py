import sys
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load .env variables
load_dotenv()

from utils.ai import generate_project_brief

def test_generation():
    print("Testing OpenRouter Integration...")
    
    # Mock project data
    mock_project = {
        "title": "Eco-Friendly Urban Mobility",
        "description": "This project aims to reduce carbon emissions in urban areas by implementing a network of electric autonomous shuttles.",
        "objective": "To develop a scalable algorithm for routing autonomous vehicles in high-density traffic zones while minimizing energy consumption."
    }
    
    # Check for API Key
    if not os.getenv("OPENROUTER_API_KEY"):
        print("⚠️  OPENROUTER_API_KEY is missing from environment!")
        print("Please set it in your .env file or export it.")
        return

    print(f"Generating brief for: {mock_project['title']}...")
    # You can change the model here if you want to test Gemini 3.0 specifically
    # model="google/gemini-2.0-flash-exp:free" (default)
    brief = generate_project_brief(mock_project)
    
    if brief:
        print("\n✅ Success! Generated Brief:\n")
        print("="*40)
        print(brief)
        print("="*40)
    else:
        print("\n❌ Failed to generate brief. Check logs.")

if __name__ == "__main__":
    test_generation()
