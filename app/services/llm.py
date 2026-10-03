from openai import OpenAI

from app.core.config import settings

SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer the user's question using ONLY the "
    "provided context. If the answer is not in the context, say you don't know."
)


def build_messages(question: str, chunks: list[str]) -> list[dict]:
    context = "\n\n".join(f"[{i + 1}] {c}" for i, c in enumerate(chunks))
    user_prompt = f"Context:\n{context}\n\nQuestion: {question}"
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def generate_answer(question: str, chunks: list[str]) -> str:
    client = OpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=build_messages(question, chunks),
        temperature=0.2,
    )
    return response.choices[0].message.content