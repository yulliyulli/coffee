"""
데이터베이스 모델 정의 (동기 버전)
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session
from datetime import datetime
import json
import os

Base = declarative_base()

class Order(Base):
    """주문 테이블"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True, index=True)  # 주문번호
    customer_name = Column(String(100), index=True)  # 고객명
    created_at = Column(DateTime, default=datetime.now)  # 주문시간
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 수정시간
    
    # 주문 아이템들과의 관계
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    """주문 아이템 테이블"""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))  # 주문 FK
    drink_name = Column(String(200))  # 음료명
    options_json = Column(Text)  # 옵션들 (JSON 형태로 저장)
    created_at = Column(DateTime, default=datetime.now)
    
    # 주문과의 관계
    order = relationship("Order", back_populates="items")
    
    @property
    def options(self):
        """옵션을 딕셔너리로 반환"""
        if self.options_json:
            return json.loads(self.options_json)
        return {}
    
    @options.setter
    def options(self, value):
        """옵션을 JSON 문자열로 저장"""
        self.options_json = json.dumps(value, ensure_ascii=False)

# 데이터베이스 설정
def get_database_url():
    """데이터베이스 URL 생성"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'data', 'coffee_orders.db')
    
    # data 디렉토리 생성
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    return f"sqlite:///{db_path}"

# 동기 데이터베이스 엔진
DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """테이블 생성"""
    Base.metadata.create_all(bind=engine)
    print("✅ 데이터베이스 테이블이 생성되었습니다.")

def get_db():
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
