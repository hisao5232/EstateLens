import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, init_db, Property
import scraper
import processor

app = FastAPI(title="EstateLens API")

# DBセッションの依存注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    init_db()  # 起動時にテーブルを作成

@app.get("/")
def index():
    return {"project": "EstateLens", "status": "active"}

@app.post("/scrape")
async def run_scraping():
    # scraper.py の全件取得ロジックを呼び出す
    results = await scraper.fetch_data()
    
    if not results:
        return {"status": "error", "message": "Failed to fetch data"}
    
    # 最初の5件だけをピックアップして、中身を分かりやすく返す
    return {
        "status": "success",
        "total_count": len(results),
        "sample_data": results[:5]  # 最初の5件
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
