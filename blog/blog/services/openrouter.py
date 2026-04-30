import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class OpenRouterClient:
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, model="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free", temperature=0.7, max_tokens=200):
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def generate(self, prompt):
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        response = requests.post(
            self.BASE_URL,
            headers=self._headers(),
            json=payload,
            timeout=15
        )
        logger.debug("Received response from OpenRouter", extra={
            "status_code": response.status_code
        })
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        logger.info("OpenRouter generation successful")

        return content

    def summarize_post(self, title, content):
        logger.info("Generating summary for post", extra={
            "title": title[:50]
        })

        prompt = f"""
        Generate a concise summary (2-3 lines):

        Title: {title}
        Content: {content}
        """

        return self.generate(prompt)