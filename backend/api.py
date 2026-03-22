import uvicorn
from fastapi import FastAPI, Depends, HTTPException
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
    init_db()  # 起動時にテーブルを作成（初回のみ）

@app.get("/")
def index():
    return {"project": "EstateLens", "status": "active"}

@app.post("/scrape")
async def run_scraping(db: Session = Depends(get_db)):
    # 1. scraper.py で生データを取得
    raw_data = await scraper.fetch_data()
    
    if not raw_data:
        raise HTTPException(status_code=500, detail="Failed to fetch data")
    
    # 2. processor.py で数値をクリーニング
    cleaned_df = processor.clean_properties(raw_data)
    
    # 3. データベースへ保存（重複チェック付き）
    new_records_count = 0
    for _, row in cleaned_df.iterrows():
        # 詳細URLをキーに、既にDBにあるか確認
        exists = db.query(Property).filter(Property.url == row.get('detail_url')).first()
        
        if not exists:
            db_property = Property(
                title=row['title'],
                rent=row['rent_num'],
                admin_fee=row['admin_num'],
                age=row['age_num'],
                area=row['area_num'],
                station_dist=row['walk_num'],
                address=row.get('address', 'N/A'),
                url=row['detail_url']
            )
            db.add(db_property)
            new_records_count += 1
            
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database commit failed")
    
    return {
        "status": "success",
        "total_scraped": len(raw_data),
        "new_records_saved": new_records_count,
        "message": f"Processed {new_records_count} new records."
    }

@app.get("/properties")
def get_properties(db: Session = Depends(get_db)):
    # データベースから最新の5件を取得
    properties = db.query(Property).order_by(Property.id.desc()).limit(5).all()
    return properties
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
