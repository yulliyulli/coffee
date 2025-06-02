#!/bin/bash
# SQLite 동기 버전 설치 및 실행 스크립트

echo "🗄️ SQLite 기반 카페 주문 시스템 설치 중... (동기 버전)"

# 가상환경 활성화 확인
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "📦 가상환경 활성화 중..."
    source .venv/bin/activate
fi

# 의존성 설치
echo "📦 의존성 설치 중..."
pip install -r requirements.txt

echo "✅ 설치 완료!"
echo ""
echo "🚀 서버를 시작하려면:"
echo "   python app.py"
echo ""
echo "🛠️ 데이터베이스 관리 도구:"
echo "   python db_manager.py"
echo ""
echo "📊 API 문서: http://localhost:8000/docs"
echo "📈 통계 API: http://localhost:8000/api/stats"
echo "🧪 동시성 테스트: db_manager.py → 6번 선택"
