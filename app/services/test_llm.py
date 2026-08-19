from app.services.llm import ask_llm


response = ask_llm(
    "Explain in one sentence why data cleaning is important."
)


print(response)