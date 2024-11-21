from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.post("/webhook")
async def webhook(request: Request):
    signature = request.headers['X-Line-Signature']
    body = await request.body()
    
    try:
        handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    
    # GPT評估提示
    prompt = f"""
    請評估以下英文寫作，並提供：
    1. CEFR等級評估（B2/C1）
    2. 詳細評分（滿分100）
    3. 具體改進建議，以達到C1和學術寫作標準
    
    學生寫作內容：
    {text}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    
    feedback = response.choices[0].message.content
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=feedback)
    )