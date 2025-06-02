#!/usr/bin/env python3
"""
디버깅 및 테스트용 스크립트
"""

import os
import json
from datetime import datetime

def check_data_folder():
    """데이터 폴더 상태 확인"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, 'data')
    orders_file = os.path.join(data_dir, 'orders.json')
    
    print("=== 데이터 폴더 상태 확인 ===")
    print(f"현재 디렉토리: {current_dir}")
    print(f"데이터 디렉토리: {data_dir}")
    print(f"데이터 디렉토리 존재: {os.path.exists(data_dir)}")
    print(f"주문 파일 경로: {orders_file}")
    print(f"주문 파일 존재: {os.path.exists(orders_file)}")
    
    if os.path.exists(orders_file):
        file_size = os.path.getsize(orders_file)
        print(f"파일 크기: {file_size} bytes")
        
        if file_size == 0:
            print("❌ 파일이 비어있습니다!")
            return
            
        try:
            with open(orders_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    print("❌ 파일 내용이 비어있습니다!")
                    return
                    
                orders = json.loads(content)
                print(f"✅ 주문 데이터 개수: {len(orders)}")
                
                for i, order in enumerate(orders):
                    customer_name = order.get('customer_name', '이름없음')
                    items_count = len(order.get('items', []))
                    order_id = order.get('order_id', '없음')
                    print(f"  {i+1}. {customer_name} - {items_count}개 음료 (ID: {order_id})")
                    
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 오류: {e}")
            print("파일이 손상되었습니다. 복구가 필요합니다.")
            
            # 손상된 파일 내용 보여주기
            with open(orders_file, 'r', encoding='utf-8') as f:
                damaged_content = f.read()
                print(f"손상된 파일 내용 (처음 200자):")
                print(repr(damaged_content[:200]))
                
        except Exception as e:
            print(f"❌ 파일 읽기 오류: {e}")
    
    print()

def create_test_data():
    """테스트 데이터 생성"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, 'data')
    orders_file = os.path.join(data_dir, 'orders.json')
    
    # 데이터 디렉토리 생성
    os.makedirs(data_dir, exist_ok=True)
    
    test_orders = [
        {
            "order_id": "20241201_120000",
            "customer_name": "김민수",
            "items": [
                {
                    "name": "아메리카노",
                    "options": {
                        "size": "Grande",
                        "temperature": "Hot",
                        "shot": "기본",
                        "syrup": "없음"
                    }
                }
            ],
            "timestamp": datetime.now().isoformat()
        },
        {
            "order_id": "20241201_120100",
            "customer_name": "이영희",
            "items": [
                {
                    "name": "카페 라떼",
                    "options": {
                        "size": "Venti",
                        "temperature": "Iced",
                        "milk": "오트 밀크",
                        "shot": "1샷 추가",
                        "syrup": "바닐라"
                    }
                },
                {
                    "name": "자바칩 프라푸치노",
                    "options": {
                        "size": "Grande",
                        "milk": "일반 우유",
                        "shot": "기본",
                        "whip": "기본",
                        "syrup": "없음"
                    }
                }
            ],
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    with open(orders_file, 'w', encoding='utf-8') as f:
        json.dump(test_orders, f, ensure_ascii=False, indent=2)
    
    print("✅ 테스트 데이터가 생성되었습니다!")
    print(f"파일 위치: {orders_file}")

def fix_damaged_file():
    """손상된 JSON 파일 복구"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    orders_file = os.path.join(current_dir, 'data', 'orders.json')
    
    if not os.path.exists(orders_file):
        print("❌ 주문 파일이 없습니다.")
        return
    
    print("🔧 손상된 파일 복구 시도...")
    
    # 백업 파일 생성
    backup_file = orders_file + '.backup.' + datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        with open(orders_file, 'rb') as src, open(backup_file, 'wb') as dst:
            dst.write(src.read())
        print(f"✅ 백업 파일 생성: {backup_file}")
    except Exception as e:
        print(f"❌ 백업 실패: {e}")
        return
    
    # 빈 배열로 초기화
    try:
        with open(orders_file, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        print(f"✅ 파일이 빈 배열로 초기화되었습니다.")
        print(f"📝 백업 파일: {backup_file}")
    except Exception as e:
        print(f"❌ 복구 실패: {e}")


def clear_all_orders():
    """모든 주문 데이터 삭제"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    orders_file = os.path.join(current_dir, 'data', 'orders.json')
    
    if os.path.exists(orders_file):
        os.remove(orders_file)
        print("✅ 모든 주문 데이터가 삭제되었습니다!")
    else:
        print("❌ 삭제할 주문 데이터가 없습니다.")

if __name__ == "__main__":
    print("🔧 카페 주문 시스템 디버깅 도구")
    print("1. 데이터 폴더 상태 확인")
    print("2. 테스트 데이터 생성")
    print("3. 손상된 파일 복구")
    print("4. 모든 주문 데이터 삭제")
    print("5. 종료")
    
    while True:
        choice = input("\n선택하세요 (1-5): ").strip()
        
        if choice == "1":
            check_data_folder()
        elif choice == "2":
            create_test_data()
        elif choice == "3":
            fix_damaged_file()
        elif choice == "4":
            clear_all_orders()
        elif choice == "5":
            print("👋 종료합니다.")
            break
        else:
            print("❌ 잘못된 선택입니다. 1-5 중에서 선택해주세요.")
