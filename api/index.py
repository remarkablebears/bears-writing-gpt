from fastapi import FastAPI, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from mangum import Mangum

# 創建 FastAPI 應用
app = FastAPI()

# 設定 Line Bot
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/api/callback")
async def callback(request: Request):
    try:
        # 直接回應，確認 webhook 可以運作
        return "OK"
    except Exception as e:
        print(f"Error: {str(e)}")
        return "Error"

# Mangum handler
handler = Mangum(app)