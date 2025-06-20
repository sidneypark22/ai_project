from openai import OpenAI
from typing import List
from pydantic import BaseModel, Field
import base64
import os
from dotenv import load_dotenv
load_dotenv()

class OpenAIClientHelper:
    def __init__(self, base_url: str | None = None, api_key: str | None = None, llm_options: dict = {}) -> OpenAI:
        self.base_url = base_url or os.getenv("OPENAI_API_BASE_URL")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY"),
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )
        self.llm_options = {
            "temperature": 0.0,
            "top_p": 0.0,
        } if llm_options == {} else llm_options

    def chat_completion_create(self, model: str, messages: list, temperature: float = 0.7, **kwargs) -> dict:
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            **self.llm_options,
            **kwargs
        )
    
    def chat_completion_parse(self, model: str, messages: list[dict], response_format: BaseModel | None = None):
        return self.client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            response_format=response_format,
            **self.llm_options
        )

    def completion(self, model: str, prompt: str, max_tokens: int = 100, temperature: float = 0.7):
        return self.client.Completion.create(
            model=model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
    
    def create_embedding(self, model: str, input: str) -> list[float]:
        return self.client.Embedding.create(
            model=model,
            input=input
        ).data[0].embedding
    
    def get_image_base64(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def append_image_prompt_to_messages(self, messages: list, prompt: str, image_base64: str) -> list[dict]:
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt,
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    },
                },
            ],
        })
        return messages
