import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert

# .env から読み込まれる環境変数
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)            # 物件名
    rent = Column(Float)             # 家賃（万円）
    admin_fee = Column(Float)        # 管理費（万円）
    address = Column(String)         # 住所
    age = Column(Integer)            # 築年数（新築=0）
    area = Column(Float)             # 面積（㎡）
    station_dist = Column(Integer)   # 駅徒歩（分）
    url = Column(String, unique=True) # 重複取得防止用URL
    layout = Column(String)          # 間取り（例: 1K, 2LDK）
    created_at = Column(DateTime, default=datetime.now)

# テーブル作成用関数
def init_db():
    Base.metadata.create_all(bind=engine)

def save_properties(db, properties_data):
    """
    PandasのDataFrameや辞書のリストを受け取り、
    URLが重複していれば更新、なければ挿入（Upsert）します。
    """
    for item in properties_data:
        # PostgreSQLのUPSERT (ON CONFLICT DO UPDATE) を使用
        stmt = insert(Property).values(**item)
        stmt = stmt.on_conflict_do_update(
            index_elements=['url'], # URLがユニーク制約である必要があります
            set_=item
        )
        db.execute(stmt)
    db.commit()
    