import json

from groq import AsyncGroq

from config import Settings
from models import SearchResult

SYSTEM_PROMPT = (
    "You are a helpful service provider search assistant. "
    "When the user searches for a service provider (prestataire), present the results "
    "in a natural, conversational way. Highlight the provider's name, specialty, "
    "location, services offered, rating, and hourly rate. Explain why each provider "
    "might be a good match for the user's needs. Be concise and helpful. "
    "Respond in the same language as the user's query."
)


class ChatService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.client = AsyncGroq(api_key=self.settings.GROQ_API_KEY)
        self.model = self.settings.GROQ_MODEL

    def _format_results(self, results: list[SearchResult]) -> str:
        items = []
        for r in results:
            items.append({
                "name": r.prestataire.name,
                "specialty": r.prestataire.specialty,
                "description": r.prestataire.description,
                "services": r.prestataire.services,
                "city": r.prestataire.city,
                "country": r.prestataire.country,
                "hourly_rate": r.prestataire.hourly_rate,
                "rating": r.prestataire.rating,
                "similarity_score": round(r.similarity_score, 3),
            })
        return json.dumps(items, ensure_ascii=False)

    async def generate_response(
        self, user_message: str, search_results: list[SearchResult]
    ) -> str:
        results_json = self._format_results(search_results)
        user_content = (
            f"User query: {user_message}\n\n"
            f"Search results (JSON):\n{results_json}"
        )

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            stream=False,
        )
        return response.choices[0].message.content

    async def generate_response_stream(
        self, user_message: str, search_results: list[SearchResult]
    ):
        results_json = self._format_results(search_results)
        user_content = (
            f"User query: {user_message}\n\n"
            f"Search results (JSON):\n{results_json}"
        )

        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content
