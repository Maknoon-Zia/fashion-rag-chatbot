from groq import Groq
from app.core.config import get_settings

def main() -> None:
    s = get_settings()
    models = Groq(api_key=s.groq_api_key).models.list().data
    print(f"Current LLM_MODEL: {s.llm_model}\nAvailable to your key:")
    for m in sorted(models, key=lambda m: m.id):
        print(f"  {m.id}")

if __name__ == "__main__":
    main()