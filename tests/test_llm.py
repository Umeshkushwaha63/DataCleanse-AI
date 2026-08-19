from app.services.llm import ask_llm


def main():
    response = ask_llm("Say Hello in one sentence.")
    print(response)


if __name__ == "__main__":
    main()