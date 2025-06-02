"""
카페 주문 시스템 - 최종 버전
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
import yaml
import json
from datetime import datetime
from typing import List, Dict
import os
import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from database import get_db, create_tables, Order, OrderItem

# FastAPI 앱 생성 (docs_url=None으로 API 문서 비활성화)
app = FastAPI(
    title="카페 주문 시스템", 
    description="카페 주문 시스템 백엔드",
    docs_url=None,  # Swagger UI 비활성화
    redoc_url=None  # ReDoc 비활성화
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 애플리케이션 시작 시 테이블 생성
@app.on_event("startup")
def startup_event():
    """앱 시작 시 데이터베이스 초기화"""
    create_tables()
    print("🚀 카페 주문 시스템이 시작되었습니다")

def load_menu():
    """메뉴 파일 로드"""
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    menu_path = os.path.join(current_dir, 'config', 'menu.yml')
    
    with open(menu_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

@app.get("/api/menu")
def get_menu():
    """메뉴 조회"""
    return load_menu()

@app.get("/api/orders/{customer_name}")
def get_customer_orders(customer_name: str, db: Session = Depends(get_db)):
    """특정 고객의 주문 내역 조회"""
    try:
        # 고객의 주문들을 조회 (아이템들과 함께)
        orders = db.query(Order).filter(
            Order.customer_name == customer_name
        ).order_by(Order.created_at.desc()).all()
        
        # JSON 형태로 변환
        orders_data = []
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
            
            orders_data.append(order_dict)
        
        return {"orders": orders_data, "count": len(orders_data)}
        
    except Exception as e:
        print(f"주문 조회 오류: {e}")
        return {"orders": [], "count": 0}

@app.delete("/api/orders/{customer_name}")
def delete_customer_orders(customer_name: str, db: Session = Depends(get_db)):
    """특정 고객의 모든 주문 삭제"""
    try:
        # 고객의 모든 주문 조회
        orders = db.query(Order).filter(Order.customer_name == customer_name).all()
        
        if not orders:
            return {"status": "success", "message": f"{customer_name}님의 주문이 삭제되었습니다."}
        
        # 주문들 삭제 (CASCADE로 OrderItem들도 자동 삭제됨)
        for order in orders:
            db.delete(order)
        
        db.commit()
        print(f"✅ {customer_name}님의 {len(orders)}개 주문이 삭제되었습니다.")
        
        return {"status": "success", "message": f"{customer_name}님의 주문이 삭제되었습니다."}
        
    except Exception as e:
        db.rollback()
        print(f"주문 삭제 오류: {e}")
        return {"status": "error", "message": "주문 삭제에 실패했습니다."}

@app.post("/api/orders/{customer_name}/items")
def add_item_to_order(
    customer_name: str, 
    item_data: Dict, 
    db: Session = Depends(get_db)
):
    """기존 주문에 아이템 추가 또는 새 주문 생성"""
    try:
        print(f"📝 {customer_name}님의 주문 처리 시작: {item_data}")
        
        # 해당 고객의 가장 최근 주문 찾기
        existing_order = db.query(Order).filter(
            Order.customer_name == customer_name
        ).order_by(Order.created_at.desc()).first()
        
        if existing_order:
            # 기존 주문에 아이템 추가
            new_item = OrderItem(
                order_id=existing_order.id,
                drink_name=item_data["name"],
                options=item_data.get("options", {})
            )
            db.add(new_item)
            
            # 주문 수정 시간 업데이트
            existing_order.updated_at = datetime.now()
            
            print(f"📝 기존 주문에 추가: {item_data['name']}")
            
        else:
            # 새 주문 생성
            order_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:17]  # 마이크로초 포함
            
            new_order = Order(
                order_id=order_id,
                customer_name=customer_name
            )
            db.add(new_order)
            db.flush()  # ID 생성을 위해
            
            # 주문 아이템 추가
            new_item = OrderItem(
                order_id=new_order.id,
                drink_name=item_data["name"],
                options=item_data.get("options", {})
            )
            db.add(new_item)
            
            print(f"📝 새 주문 생성: {customer_name} - {item_data['name']}")
        
        db.commit()
        print(f"✅ 주문 저장 완료: {customer_name}")
        
        return {"status": "success", "message": "주문에 아이템이 추가되었습니다."}
        
    except Exception as e:
        db.rollback()
        print(f"❌ 주문 저장 실패: {e}")
        return {"status": "error", "message": f"주문 저장에 실패했습니다: {str(e)}"}

@app.get("/api/admin/orders")
def get_admin_orders(db: Session = Depends(get_db)):
    """관리자용 전체 주문 내역 조회 - 개선된 버전"""
    try:
        orders = db.query(Order).order_by(Order.created_at.desc()).all()
        
        orders_data = []
        customers_summary = {}
        total_customers = set()
        
        for order in orders:
            customer_name = order.customer_name
            total_customers.add(customer_name)
            
            # 고객별 요약 정보 생성
            if customer_name not in customers_summary:
                customers_summary[customer_name] = {
                    "customer_name": customer_name,
                    "order_count": 0,
                    "total_items": 0,
                    "items_list": [],
                    "last_order_date": None,
                    "orders_summary": []
                }
            
            # 주문 아이템들을 문자열로 변환
            items_text = []
            for item in order.items:
                options_text = []
                for key, value in item.options.items():
                    options_text.append(f"{key}: {value}")
                
                if options_text:
                    item_text = f"{item.drink_name} ({', '.join(options_text)})"
                else:
                    item_text = item.drink_name
                items_text.append(item_text)
                
                # 고객별 아이템 리스트에 추가
                customers_summary[customer_name]["items_list"].append(item_text)
            
            # 고객별 주문 통계 업데이트
            customers_summary[customer_name]["order_count"] += 1
            customers_summary[customer_name]["total_items"] += len(order.items)
            customers_summary[customer_name]["last_order_date"] = order.created_at.strftime("%Y-%m-%d %H:%M")
            customers_summary[customer_name]["orders_summary"].append({
                "order_id": order.order_id,
                "items": items_text,
                "date": order.created_at.strftime("%Y-%m-%d %H:%M")
            })
            
            order_dict = {
                "id": order.id,
                "order_id": order.order_id,
                "customer_name": order.customer_name,
                "items_text": " | ".join(items_text),
                "items_count": len(order.items),
                "order_date": order.created_at.strftime("%Y-%m-%d"),
                "order_time": order.created_at.strftime("%H:%M:%S"),
                "timestamp": order.created_at.isoformat()
            }
            
            orders_data.append(order_dict)
        
        # 고객별 요약 데이터 정리
        customers_list = []
        for customer_data in customers_summary.values():
            # 고객의 모든 주문 아이템들을 한 줄로 표시
            all_items = " | ".join(customer_data["items_list"])
            customers_list.append({
                "customer_name": customer_data["customer_name"],
                "order_count": customer_data["order_count"],
                "total_items": customer_data["total_items"],
                "all_items_summary": all_items,
                "last_order_date": customer_data["last_order_date"],
                "orders_detail": customer_data["orders_summary"]
            })
        
        # 주문 수가 많은 고객 순으로 정렬
        customers_list.sort(key=lambda x: x["order_count"], reverse=True)
        
        return {
            "orders": orders_data,
            "customers_summary": customers_list,
            "total_orders": len(orders_data),
            "total_customers": len(total_customers),
            "total_items": sum(order["items_count"] for order in orders_data)
        }
        
    except Exception as e:
        print(f"전체 주문 조회 오류: {e}")
        return {
            "orders": [],
            "customers_summary": [],
            "total_orders": 0,
            "total_customers": 0,
            "total_items": 0
        }

@app.get("/api/admin/orders/excel")
def download_orders_excel(db: Session = Depends(get_db)):
    """주문 내역 엑셀 다운로드"""
    try:
        orders = db.query(Order).order_by(Order.created_at.desc()).all()
        
        # 엑셀 워크북 생성
        wb = Workbook()
        ws = wb.active
        ws.title = "주문 내역"
        
        # 헤더 스타일
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        center_alignment = Alignment(horizontal="center", vertical="center")
        
        # 헤더 작성
        headers = ["번호", "주문번호", "고객명", "주문내용", "음료수", "주문일", "주문시간"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_alignment
        
        # 데이터 작성
        for row_num, order in enumerate(orders, 2):
            # 주문 아이템들을 문자열로 변환
            items_text = []
            for item in order.items:
                options_text = []
                for key, value in item.options.items():
                    options_text.append(f"{key}: {value}")
                
                if options_text:
                    item_text = f"{item.drink_name} ({', '.join(options_text)})"
                else:
                    item_text = item.drink_name
                items_text.append(item_text)
            
            # 데이터 입력
            ws.cell(row=row_num, column=1, value=row_num-1)  # 번호
            ws.cell(row=row_num, column=2, value=order.order_id)  # 주문번호
            ws.cell(row=row_num, column=3, value=order.customer_name)  # 고객명
            ws.cell(row=row_num, column=4, value=" | ".join(items_text))  # 주문내용
            ws.cell(row=row_num, column=5, value=len(order.items))  # 음료수
            ws.cell(row=row_num, column=6, value=order.created_at.strftime("%Y-%m-%d"))  # 주문일
            ws.cell(row=row_num, column=7, value=order.created_at.strftime("%H:%M:%S"))  # 주문시간
        
        # 열 너비 자동 조정
        column_widths = [8, 20, 15, 50, 10, 12, 12]
        for col, width in enumerate(column_widths, 1):
            ws.column_dimensions[ws.cell(row=1, column=col).column_letter].width = width
        
        # 메모리에서 엑셀 파일 생성
        excel_file = io.BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)
        
        # 파일명 생성 (현재 날짜 포함)
        filename = f"주문내역_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # 스트리밍 응답으로 반환
        def generate():
            yield excel_file.read()
        
        return StreamingResponse(
            generate(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        print(f"엑셀 다운로드 오류: {e}")
        raise HTTPException(status_code=500, detail="엑셀 파일 생성에 실패했습니다.")

if __name__ == "__main__":
    import uvicorn
    print("🚀 카페 주문 시스템 백엔드를 시작합니다...")
    print("🔗 키오스크: http://localhost:5173")
    print("📊 관리자: http://localhost:5173/admin")
    print("🛑 종료하려면 Ctrl+C를 누르세요")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
