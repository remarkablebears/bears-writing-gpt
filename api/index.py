from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 創建 FastAPI 應用
app = FastAPI()

# 設定 Line Bot
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# 設定 OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# 健康檢查路由
@app.get("/")
async def health_check():
    return {"status": "OK"}

# Line Bot webhook 路由
@app.post("/api/callback")
async def callback(request: Request):
    # 獲取 X-Line-Signature header 值
    signature = request.headers.get('X-Line-Signature', '')
    
    # 獲取請求體
    body = await request.body()
    body = body.decode('utf-8')
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    return 'OK'

# 處理 Line 訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    
    # 呼叫 GPT 進行評分
    response = evaluate_writing(user_message)
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response)
    )

# GPT 評分函數
def evaluate_writing(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "你是一位專業的英文寫作老師，專門評分學生的英文作文並給予改進建議。"
                },
                {
                    "role": "user",
                    "content": f"""請評估這篇英文作文，給出：
1. CEFR等級(B2/C1)
2. 分數（滿分100）
3. 優點
4. 需要改進的地方
5. 具體改進建議

作文內容：
{text}"""
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"抱歉，評分時發生錯誤：{str(e)}"