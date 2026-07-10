import os

from openai import OpenAI

from ingestion import get_chroma_collection
from database import insert_chat_message, get_chat_history

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions based on the provided context. "
    "If the answer is not in the context, say so clearly. "
    "Always respond in the same language as the user's question."
)


def get_openai_client():
    return OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        base_url=os.environ.get("OPENAI_BASE_URL"),
    )


def retrieve_chunks(query, document_id, n_results=5):
    collection = get_chroma_collection()
    kwargs = {"query_texts": [query], "n_results": n_results}
    if document_id:
        kwargs["where"] = {"document_id": document_id}

    results = collection.query(**kwargs)
    return results["documents"][0] if results["documents"] else []


def chat(message, document_id):
    chunks = retrieve_chunks(message, document_id)

    context = "\n\n---\n\n".join(chunks) if chunks else "No relevant context found."

    history = get_chat_history(document_id, limit=10)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.append({
        "role": "system",
        "content": f"Context from uploaded documents:\n\n{context}",
    })
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})

    client = get_openai_client()
    response = client.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        messages=messages,
    )
    answer = response.choices[0].message.content

    insert_chat_message(document_id, "user", message)
    insert_chat_message(document_id, "assistant", answer)

    return answer
