@app.post("/api/callback")
async def callback(request: Request):
    # 直接返回 OK，確保快速響應
    return 'OK'