import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Vercel uchun database path
def get_database_url():
    if os.getenv("VERCEL"):
        # Vercel'da /tmp ishlatish
        return "sqlite:///./tmp/trade_data.db"
    else:
        # Local development
        os.makedirs("./database", exist_ok=True)
        return "sqlite:///./database/trade_data.db"

DATABASE_URL = get_database_url()

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=False  # SQL query'larni ko'rsatmaslik uchun
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TradeRecord(Base):
    __tablename__ = "trade_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hs_2_code = Column(String(2), index=True)
    hs_4_code = Column(String(4), index=True)
    hs_6_code = Column(String(6), index=True)
    hs_10_code = Column(String(10), index=True)
    product_name = Column(String(500))
    measure = Column(String(50))
    export_volume = Column(Float)
    export_price = Column(Float)
    import_volume = Column(Float)
    import_price = Column(Float)
    trading_partner = Column(String(100))
    year = Column(Integer, index=True)
    hs_group = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)

# Database yaratish
def init_database():
    try:
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")

# Database initialization
init_database()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD operatsiyalar uchun utility functions
def create_trade_record(db, trade_data):
    try:
        db_record = TradeRecord(**trade_data)
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    except Exception as e:
        db.rollback()
        raise e

def delete_trade_record(db, record_id):
    try:
        record = db.query(TradeRecord).filter(TradeRecord.id == record_id).first()
        if record:
            db.delete(record)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        raise e