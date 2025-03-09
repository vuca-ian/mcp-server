from fastapi import Query, FastAPI
import uvicorn
import asyncio
from typings import R
from starlette.requests import Request
from sse_starlette import EventSourceResponse
# from assistant.assistant import AiAssistant, AiOptions, AiClient
# from openai import AsyncOpenAI, OpenAI
import openai
import json
from ollama import AsyncClient, ResponseError
app = FastAPI()

class Hello:
   name: str



RETRY_TIMEOUT = 15000
# assistant = AiAssistant(AiClient)
error503 = "OpenAI server is busy, try again later"

client = AsyncClient("http://localhost:11434")
openai.api_key  ="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"
openai.base_url ="https://openrouter.ai/api/v1"
async def generate_stream(prompt: str, model: str = "qwen2.5-coder:14b"):
    """
    生成器函数，用于流式获取 Ollama 响应
    """
    try:
        # 发起异步生成请求
        response = await client.generate(
            model=model,
            prompt=prompt,
            stream=True  # 关键：启用流式模式
        )
        
        # 流式读取响应
        async for chunk in response:
            if chunk["done"]: break
            yield f"data: {json.dumps(chunk['response'],ensure_ascii=False)}\n\n"
            
    except ResponseError as e:
        yield f"data: [API Error: {e.error}]\n\n"
    except Exception as e:
        yield f"data: [System Error: {str(e)}]\n\n"
@app.get("/sse")
async def sse_stream(query:str= Query(..., max_length=20)):
   """
    Create a marketing campaign plan for the brand name entered in the prompt
    """
   """
    SSE 流式响应端点
    """
   return EventSourceResponse(
        generate_stream(query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )
def main():
   uvicorn.run(app,host="0.0.0.0",port=8001)

if __name__ == "__main__":
   main()