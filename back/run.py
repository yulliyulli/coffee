#!/usr/bin/env python3
"""
카페 주문 시스템 백엔드 실행 스크립트
"""

if __name__ == "__main__":
    import uvicorn
    from app import app
    
    print("🚀 카페 주문 시스템 백엔드를 시작합니다...")
    print("🔗 키오스크: http://localhost:5173")
    print("📊 관리자: http://localhost:5173/admin")
    print("🛑 종료하려면 Ctrl+C를 누르세요")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
