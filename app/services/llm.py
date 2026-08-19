import os

from dotenv import load_dotenv
from groq import Groq


# =====================================================
# LOAD ENVIRONMENT VARIABLES
# =====================================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")


# =====================================================
# CHECK API KEY
# =====================================================

if not api_key:

    raise ValueError(
        "GROQ_API_KEY was not found.\n"
        "Please check your .env file."
    )


# =====================================================
# CREATE GROQ CLIENT
# =====================================================

client = Groq(
    api_key=api_key,
    timeout=60.0
)


# =====================================================
# AI FUNCTION
# =====================================================

def ask_llm(prompt: str) -> str:

    try:

        response = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert Data Analyst "
                        "and Data Quality Engineer. "
                        "Give clear, practical and safe "
                        "recommendations."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.2,

            max_tokens=2000,

            include_reasoning=False,

            stream=False
        )

        return response.choices[0].message.content


    except Exception as e:

        print(
            "LLM ERROR:",
            str(e)
        )

        return (
            "AI service is temporarily unavailable.\n\n"
            "The dataset scan was completed successfully, "
            "but the AI recommendation could not be generated.\n\n"
            f"Technical error: {str(e)}"
        )