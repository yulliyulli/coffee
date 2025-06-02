#!/usr/bin/env python3
"""
SQLite 기반 디버깅 및 관리 도구 (동기 버전)
"""

import os
import json
from datetime import datetime
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker
from database import Order, OrderItem, Base, get_database_url

class DatabaseManager:
    def __init__(self):
        self.database_url = get_database_url()
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def check_database_status(self):
        """데이터베이스 상태 확인"""
        print("=== SQLite 데이터베이스 상태 확인 ===")
        
        db_file_path = self.database_url.replace("sqlite:///", "")
        print(f"데이터베이스 파일: {db_file_path}")
        print(f"파일 존재: {os.path.exists(db_file_path)}")
        
        if os.path.exists(db_file_path):
            file_size = os.path.getsize(db_file_path)
            print(f"파일 크기: {file_size} bytes")
        
        try:
            # 테이블 존재 확인
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name IN ('orders', 'order_items')
                """))
                tables = [row[0] for row in result.fetchall()]
                print(f"존재하는 테이블: {tables}")
                
                if 'orders' in tables:
                    # 주문 통계
                    result = conn.execute(text("SELECT COUNT(*) FROM orders"))
                    order_count = result.fetchone()[0]
                    print(f"총 주문 수: {order_count}")
                    
                    result = conn.execute(text("SELECT COUNT(DISTINCT customer_name) FROM orders"))
                    customer_count = result.fetchone()[0]
                    print(f"고유 고객 수: {customer_count}")
                
                if 'order_items' in tables:
                    result = conn.execute(text("SELECT COUNT(*) FROM order_items"))
                    item_count = result.fetchone()[0]
                    print(f"총 주문 아이템 수: {item_count}")
                    
                    # 인기 음료 TOP 5
                    result = conn.execute(text("""
                        SELECT drink_name, COUNT(*) as count 
                        FROM order_items 
                        GROUP BY drink_name 
                        ORDER BY count DESC 
                        LIMIT 5
                    """))
                    popular_drinks = result.fetchall()
                    if popular_drinks:
                        print("인기 음료 TOP 5:")
                        for i, (drink, count) in enumerate(popular_drinks, 1):
                            print(f"  {i}. {drink}: {count}번 주문")
        
        except Exception as e:
            print(f"❌ 데이터베이스 접근 오류: {e}")
        
        print()

    def create_test_data(self):
        """테스트 데이터 생성"""
        try:
            with self.SessionLocal() as session:
                # 기존 데이터 확인
                existing_orders = session.query(Order).count()
                if existing_orders > 0:
                    confirm = input(f"기존 데이터가 {existing_orders}개 있습니다. 추가로 생성하시겠습니까? (y/N): ")
                    if confirm.lower() != 'y':
                        print("취소되었습니다.")
                        return
                
                # 테스트 주문 1: 김민수
                order1 = Order(
                    order_id=datetime.now().strftime("%Y%m%d_120000"),
                    customer_name="김민수"
                )
                session.add(order1)
                session.flush()
                
                item1 = OrderItem(
                    order_id=order1.id,
                    drink_name="아메리카노",
                    options={
                        "size": "Grande",
                        "temperature": "Hot",
                        "shot": "기본",
                        "syrup": "없음"
                    }
                )
                session.add(item1)
                
                # 테스트 주문 2: 이영희 (여러 아이템)
                order2 = Order(
                    order_id=datetime.now().strftime("%Y%m%d_120100"),
                    customer_name="이영희"
                )
                session.add(order2)
                session.flush()
                
                item2_1 = OrderItem(
                    order_id=order2.id,
                    drink_name="카페 라떼",
                    options={
                        "size": "Venti",
                        "temperature": "Iced",
                        "milk": "오트 밀크",
                        "shot": "1샷 추가",
                        "syrup": "바닐라"
                    }
                )
                session.add(item2_1)
                
                item2_2 = OrderItem(
                    order_id=order2.id,
                    drink_name="자바칩 프라푸치노",
                    options={
                        "size": "Grande",
                        "milk": "일반 우유",
                        "shot": "기본",
                        "whip": "기본",
                        "syrup": "없음"
                    }
                )
                session.add(item2_2)
                
                # 테스트 주문 3: 박철수 (동시성 테스트용)
                order3 = Order(
                    order_id=datetime.now().strftime("%Y%m%d_120200"),
                    customer_name="박철수"
                )
                session.add(order3)
                session.flush()
                
                item3 = OrderItem(
                    order_id=order3.id,
                    drink_name="콜드브루",
                    options={
                        "size": "Tall",
                        "syrup": "바닐라",
                        "ice": "기본"
                    }
                )
                session.add(item3)
                
                session.commit()
                print("✅ 테스트 데이터가 생성되었습니다!")
                print("- 김민수: 아메리카노 1개")
                print("- 이영희: 카페 라떼 + 자바칩 프라푸치노")
                print("- 박철수: 콜드브루 1개")
                
        except Exception as e:
            print(f"❌ 테스트 데이터 생성 실패: {e}")

    def clear_all_data(self):
        """모든 데이터 삭제"""
        try:
            with self.SessionLocal() as session:
                # 데이터 개수 확인
                order_count = session.query(Order).count()
                item_count = session.query(OrderItem).count()
                
                if order_count == 0 and item_count == 0:
                    print("❌ 삭제할 데이터가 없습니다.")
                    return
                
                confirm = input(f"정말로 모든 데이터를 삭제하시겠습니까? (주문 {order_count}개, 아이템 {item_count}개) (y/N): ")
                if confirm.lower() != 'y':
                    print("취소되었습니다.")
                    return
                
                # 모든 데이터 삭제
                session.query(OrderItem).delete()
                session.query(Order).delete()
                session.commit()
                
                print("✅ 모든 데이터가 삭제되었습니다!")
                
        except Exception as e:
            print(f"❌ 데이터 삭제 실패: {e}")

    def export_to_json(self):
        """데이터를 JSON 파일로 내보내기"""
        try:
            with self.SessionLocal() as session:
                orders = session.query(Order).all()
                
                if not orders:
                    print("❌ 내보낼 데이터가 없습니다.")
                    return
                
                export_data = []
                for order in orders:
                    order_dict = {
                        "order_id": order.order_id,
                        "customer_name": order.customer_name,
                        "timestamp": order.created_at.isoformat(),
                        "items": []
                    }
                    
                    for item in order.items:
                        item_dict = {
                            "name": item.drink_name,
                            "options": item.options
                        }
                        order_dict["items"].append(item_dict)
                    
                    export_data.append(order_dict)
                
                # 파일 저장
                export_file = f"orders_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                print(f"✅ 데이터가 {export_file}로 내보내졌습니다!")
                print(f"주문 {len(export_data)}개가 포함되었습니다.")
                
        except Exception as e:
            print(f"❌ 데이터 내보내기 실패: {e}")

    def reset_database(self):
        """데이터베이스 초기화 (테이블 재생성)"""
        try:
            confirm = input("⚠️ 데이터베이스를 완전히 초기화하시겠습니까? (모든 데이터가 삭제됩니다) (y/N): ")
            if confirm.lower() != 'y':
                print("취소되었습니다.")
                return
            
            # 테이블 삭제
            Base.metadata.drop_all(bind=self.engine)
            print("✅ 기존 테이블이 삭제되었습니다.")
            
            # 테이블 재생성
            Base.metadata.create_all(bind=self.engine)
            print("✅ 새로운 테이블이 생성되었습니다.")
            
        except Exception as e:
            print(f"❌ 데이터베이스 초기화 실패: {e}")

    def stress_test(self):
        """동시성 스트레스 테스트"""
        try:
            import threading
            import time
            import random
            
            print("🧪 동시성 스트레스 테스트 시작...")
            
            def create_test_order(customer_id):
                """테스트 주문 생성"""
                try:
                    with self.SessionLocal() as session:
                        order = Order(
                            order_id=f"test_{customer_id}_{int(time.time() * 1000)}",
                            customer_name=f"테스트고객{customer_id}"
                        )
                        session.add(order)
                        session.flush()
                        
                        # 랜덤 음료 추가
                        drinks = ["아메리카노", "카페라떼", "카푸치노", "콜드브루"]
                        item = OrderItem(
                            order_id=order.id,
                            drink_name=random.choice(drinks),
                            options={"size": "Grande", "temperature": "Hot"}
                        )
                        session.add(item)
                        session.commit()
                        print(f"✅ 고객{customer_id} 주문 완료")
                        
                except Exception as e:
                    print(f"❌ 고객{customer_id} 주문 실패: {e}")
            
            # 10개의 동시 주문 생성
            threads = []
            for i in range(1, 11):
                thread = threading.Thread(target=create_test_order, args=(i,))
                threads.append(thread)
            
            # 모든 스레드 시작
            start_time = time.time()
            for thread in threads:
                thread.start()
                time.sleep(0.1)  # 약간의 지연
            
            # 모든 스레드 완료 대기
            for thread in threads:
                thread.join()
            
            end_time = time.time()
            print(f"🏁 스트레스 테스트 완료! 소요시간: {end_time - start_time:.2f}초")
            
            # 결과 확인
            with self.SessionLocal() as session:
                test_orders = session.query(Order).filter(Order.customer_name.like("테스트고객%")).count()
                print(f"📊 생성된 테스트 주문: {test_orders}개")
                
        except Exception as e:
            print(f"❌ 스트레스 테스트 실패: {e}")

def main():
    manager = DatabaseManager()
    
    print("🗄️ SQLite 데이터베이스 관리 도구 (동기 버전)")
    print("1. 데이터베이스 상태 확인")
    print("2. 테스트 데이터 생성")
    print("3. JSON으로 데이터 내보내기")
    print("4. 모든 데이터 삭제")
    print("5. 데이터베이스 완전 초기화")
    print("6. 동시성 스트레스 테스트")
    print("7. 종료")
    
    while True:
        choice = input("\n선택하세요 (1-7): ").strip()
        
        if choice == "1":
            manager.check_database_status()
        elif choice == "2":
            manager.create_test_data()
        elif choice == "3":
            manager.export_to_json()
        elif choice == "4":
            manager.clear_all_data()
        elif choice == "5":
            manager.reset_database()
        elif choice == "6":
            manager.stress_test()
        elif choice == "7":
            print("👋 종료합니다.")
            break
        else:
            print("❌ 잘못된 선택입니다. 1-7 중에서 선택해주세요.")

if __name__ == "__main__":
    main()
