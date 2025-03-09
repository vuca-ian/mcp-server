from fastapi import FastAPI, Query, HTTPException
from openai import AsyncOpenAI
from typing import Optional
import os
error503 = "OpenAI server is busy, try again later"

class AiOptions:
    type: str
    url: str
    api_key: str
client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            # api_key=os.getenv("OPENROUTER_API_KEY"),
            api_key="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"
        )
class AiClient():
    def __init__(self, option: AiOptions):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
    def chat(query: str):
        messages = [
            {"role": "user", "content": query}
        ]
        print(messages)
        try:
            response = client.chat.completions.create(
                model="qwen/qwen-plus", messages=messages,
                stream=True
                )
        except Exception as e:
            print("Error in creating campaigns from openAI:", str(e))
            raise HTTPException(503, error503)
        try:
            for chunk in response:
                current_content = chunk["choices"][0]["delta"].get("content", "")
                yield current_content
        except Exception as e:
            print("OpenAI Response (Streaming) Error: " + str(e))
            raise HTTPException(503, error503)
class AiAssistant:
    client: AiClient
    def __init__(self, client: AiClient):
        self.client = client
    
    def get_response_by_ai(self, query:str):
        print("query?", query)
        self.client.chat(self, query)