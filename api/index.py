@app.post("/api/callback")
async def callback(request: Request):
    signature = request.headers.get('X-Line-Signature', '')
    body = await request.body()
    body_str = body.decode('utf-8')
    
    try:
        # 立即回應 LINE 伺服器
        events = json.loads(body_str)["events"]
        
        # 非同步處理訊息
        for event in events:
            if event["type"] == "message" and event["message"]["type"] == "text":
                try:
                    # 取得用戶訊息
                    user_message = event["message"]["text"]
                    # 回覆訊息
                    line_bot_api.reply_message(
                        event["replyToken"],
                        TextSendMessage(text="正在評估您的作文，請稍候...")
                    )
                    # 評估寫作
                    response = evaluate_writing(user_message)
                    # 使用 push message 發送結果
                    line_bot_api.push_message(
                        event["source"]["userId"],
                        TextSendMessage(text=response)
                    )
                except Exception as e:
                    print(f"Error processing message: {str(e)}")
                    
        return "OK"
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))