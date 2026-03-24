import uvicorn
import pandas as pd
import os
import re
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, init_db, Property
import scraper
import processor

app = FastAPI(title="EstateLens API")

# --- 1. CORS設定 ---
# ローカル開発環境のNext.jsからのアクセスを許可
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://go-pro-world.net",
    "https://api-lens.go-pro-world.net",
    "https://estatelens.pages.dev"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["X-API-KEY", "Content-Type", "Authorization"],
)

# --- 2. APIキー認証の設定 ---
API_KEY = os.getenv("API_KEY")

async def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key

# --- DBセッションの依存注入 ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def index():
    return {"project": "EstateLens", "status": "active"}

@app.post("/scrape")
async def run_scraping(db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    raw_data = await scraper.fetch_data()
    if not raw_data:
        raise HTTPException(status_code=500, detail="Failed to fetch data")
    
    cleaned_df = processor.clean_properties(raw_data)
    
    new_records_count = 0
    for _, row in cleaned_df.iterrows():
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
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    
    return {
        "status": "success",
        "total_scraped": len(raw_data),
        "new_records_saved": new_records_count
    }

@app.get("/properties")
def get_properties(db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    properties = db.query(Property).order_by(Property.id.desc()).limit(50).all()
    return properties

@app.get("/analysis/stats")
def get_property_stats(db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    properties = db.query(Property).all()
    if not properties:
        return {"message": "No data available"}

    data = []
    for p in properties:
        data.append({
            "id": p.id,
            "rent": p.rent,
            "area": p.area,
            "age": p.age,
            "station_dist": p.station_dist
        })
    df = pd.DataFrame(data)
    
    df['unit_price'] = df['rent'] / df['area']
    df['age_group'] = (df['age'] // 5) * 5
    
    age_stats = df.groupby('age_group').agg({
        'rent': 'mean',
        'unit_price': 'mean',
        'id': 'count'
    }).rename(columns={'id': 'count'}).reset_index()

    return {
        "avg_rent": float(df['rent'].mean()),
        "avg_unit_price": float(df['unit_price'].mean()),
        "total_count": int(len(df)),
        "age_dist": age_stats.to_dict(orient='records')
    }

@app.get("/analysis/raw")
async def get_raw_data(db: Session = Depends(get_db)): # DBセッションを追加
    # 1. スクレイピングはせず、DBから全件取得する
    properties = db.query(Property).all()
    
    if not properties:
        return []
    
    # 2. フロントエンドが期待する形式（dict）に変換
    plot_data = []
    for p in properties:
        plot_data.append({
            "title": p.title,
            "rent_num": float(p.rent),
            "admin_num": float(p.admin_fee),
            "total_rent": float(p.rent + p.admin_fee),
            "age_num": int(p.age),
            "area_num": float(p.area),
            "walk_num": int(p.station_dist),
            "address": p.address,
            "detail_url": p.url
        })
    
    return plot_data

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
