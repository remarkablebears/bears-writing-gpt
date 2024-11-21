from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from mangum import Mangum
import openai

# 創建 FastAPI 應用
app = FastAPI()

# 設定 Line Bot
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)
openai.api_key = OPENAI_API_KEY

async def analyze_writing(text):
    try:
        response = await openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "你是一位專業的英語寫作評分老師。請依據CEFR標準評估學生的寫作，並提供從B2到C1level的具體改進建議。評分維度包括：文法準確度、詞彙運用、文章結構、學術用語等。"},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"分析過程發生錯誤: {str(e)}"

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/api/callback")
async def callback(request: Request):
    # 獲取 X-Line-Signature header 值
    signature = request.headers['X-Line-Signature']
    
    # 獲取請求體內容
    body = await request.body()
    
    try:
        # 驗證簽名
        handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    
    # 分析寫作並獲取回饋
    analysis = analyze_writing(user_message)
    
    # 發送回饋給用戶
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=analysis)
    )

# Mangum handler
handler = Mangum(app)