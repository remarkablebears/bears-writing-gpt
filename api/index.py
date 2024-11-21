from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os
from dotenv import load_dotenv
from mangum import Mangum

# 載入環境變數
load_dotenv()

# 創建 FastAPI 應用
app = FastAPI()

# 設定 Line Bot
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
webhook_handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# 設定 OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/api/callback")
async def callback(request: Request):
    # 快速回應 LINE 伺服器
    return "OK"

@app.post("/api/webhook")
async def webhook(request: Request):
    signature = request.headers.get('X-Line-Signature', '')
    body = await request.body()
    body_str = body.decode('utf-8')
    
    try:
        events = json.loads(body_str)["events"]
        for event in events:
            if event["type"] == "message" and event["message"]["type"] == "text":
                user_message = event["message"]["text"]
                user_id = event["source"]["userId"]
                
                # 先發送等待訊息
                line_bot_api.push_message(
                    user_id,
                    TextSendMessage(text="正在評估您的作文，請稍候...")
                )
                
                # 評估寫作
                try:
                    response = evaluate_writing(user_message)
                    line_bot_api.push_message(
                        user_id,
                        TextSendMessage(text=response)
                    )
                except Exception as e:
                    line_bot_api.push_message(
                        user_id,
                        TextSendMessage(text=f"抱歉，評估過程發生錯誤：{str(e)}")
                    )
        
        return "OK"
    except Exception as e:
        print(f"Error: {str(e)}")
        return "OK"

def evaluate_writing(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "你是一位專業的英文寫作老師，專門評分學生的英文作文並給予改進建議。請用繁體中文回答。"
                },
                {
                    "role": "user",
                    "content": f"""請評估這篇英文作文，給出：
1. CEFR等級(B2/C1)
2. 分數（滿分100）
3. 優點
4. 需要改進的地方
5. 具體改進建議，特別是如何提升到更高等級

作文內容：
{text}"""
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"抱歉，評分時發生錯誤：{str(e)}"

# Mangum handler
handler = Mangum(app)