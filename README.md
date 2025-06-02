# ☕ E-Book 동호회 주문 키오스크 시스템 (SQLite 버전)

Vue.js + Python FastAPI + **SQLite**로 구현한 커피숍 키오스크 주문 시스템입니다.

## 🆕 **SQLite 버전 업그레이드**

### **주요 개선사항**
- ✅ **동시성 문제 해결**: 여러 사용자가 동시에 주문해도 안전
- ✅ **데이터 무결성**: ACID 트랜잭션으로 데이터 손실 방지  
- ✅ **성능 향상**: JSON 파일 대비 훨씬 빠른 읽기/쓰기
- ✅ **확장성**: PostgreSQL 등으로 쉽게 마이그레이션 가능
- ✅ **통계 기능**: 주문 통계 및 인기 음료 분석
- ✅ **관리 도구**: GUI 기반 데이터베이스 관리 도구

## 🛠 기술 스택

### 백엔드
- **Python FastAPI** - REST API 서버
- **SQLAlchemy** - ORM (객체 관계 매핑)
- **SQLite** - 데이터베이스 (파일 기반, 동시성 지원)
- **AsyncIO** - 비동기 처리
- **PyYAML** - 메뉴 데이터 파싱

### 프론트엔드
- **Vue.js 3** - 프론트엔드 프레임워크
- **Axios** - HTTP 클라이언트
- **Vite** - 빌드 도구

## 📁 프로젝트 구조

```
coffee/
├── back/                    # 백엔드 (Python FastAPI + SQLite)
│   ├── app.py              # 메인 API 서버
│   ├── database.py         # SQLAlchemy 모델 및 DB 설정
│   ├── db_manager.py       # 데이터베이스 관리 도구
│   ├── setup_sqlite.sh     # SQLite 버전 설치 스크립트
│   ├── config/             # 설정 파일
│   │   └── menu.yml        # 메뉴 데이터
│   ├── data/               # 데이터 저장소
│   │   └── coffee_orders.db # SQLite 데이터베이스 (자동 생성)
│   ├── requirements.txt    # Python 의존성
│   └── .venv/              # Python 가상환경
├── front/                   # 프론트엔드 (Vue.js)
│   ├── src/
│   │   ├── App.vue         # 메인 컴포넌트
│   │   └── main.js         # 앱 진입점
│   ├── package.json        # 의존성 관리
│   └── vite.config.js      # Vite 설정
└── README.md
```

## 🚀 실행 방법

### 1단계: SQLite 버전으로 업그레이드

```bash
# 1. 백엔드 디렉토리로 이동
cd back

# 2. 가상환경 활성화
source .venv/bin/activate  # macOS/Linux
# 또는
.venv\Scripts\activate     # Windows

# 3. 새로운 의존성 설치
pip install -r requirements.txt

# 4. 서버 실행
python app.py
```

**또는 자동 설치 스크립트 사용:**
```bash
cd back
chmod +x setup_sqlite.sh
./setup_sqlite.sh
python app.py
```

**백엔드가 성공적으로 실행되면:**
- 🌐 API 서버: http://localhost:8000
- 📚 API 문서: http://localhost:8000/docs
- 🔗 메뉴 API: http://localhost:8000/api/menu
- 📊 통계 API: http://localhost:8000/api/stats

### 2단계: 프론트엔드 실행

새 터미널 창에서:

```bash
# 1. 프론트엔드 디렉토리로 이동
cd front

# 2. 의존성 설치 (처음 한 번만)
npm install

# 3. 개발 서버 실행
npm run dev
```

**프론트엔드가 성공적으로 실행되면:**
- 🖥️ 키오스크 UI: http://localhost:5173

## 🎯 주요 기능

### 사용자 기능
1. **이름 입력** - 주문자 이름 입력
2. **카테고리 선택** - 에스프레소, 프라푸치노, 콜드브루 등
3. **음료 선택** - 각 카테고리별 음료 선택
4. **옵션 커스터마이징** - 사이즈, 온도, 우유, 시럽 등
5. **주문 확인** - 선택한 음료와 옵션 확인
6. **주문 완료** - 주문번호 발급

## 📊 **데이터베이스 버전 새로운 기능**

### **관리 도구**
```bash
cd back
python db_manager.py
```

**기능:**
- 1. 데이터베이스 상태 확인 (테이블, 통계, 인기 음료)
- 2. 테스트 데이터 생성
- 3. JSON으로 데이터 내보내기 (백업)
- 4. 모든 데이터 삭제
- 5. 데이터베이스 완전 초기화

### **통계 API**
```bash
curl http://localhost:8000/api/stats
```

**응답 예시:**
```json
{
  "total_orders": 25,
  "total_items": 32,
  "unique_customers": 18,
  "database_type": "SQLite"
}
```

### **동시성 지원**
- ✅ **여러 사용자 동시 주문 가능**
- ✅ **ACID 트랜잭션 보장**
- ✅ **데이터 무결성 유지**
- ✅ **자동 백업 및 복구**

## 📝 메뉴 설정

`back/config/menu.yml` 파일에서 메뉴를 관리할 수 있습니다:

```yaml
categories:
  - name: "에스프레소"
    items:
      - name: "아메리카노"
        options:
          size: ["Tall", "Grande", "Venti"]
          temperature: ["Hot", "Iced"]
          # ... 기타 옵션
```

## 🔧 개발 환경 설정

### 백엔드 의존성
```bash
cd back
pip install fastapi uvicorn pyyaml
```

### 프론트엔드 의존성
```bash
cd front
npm install vue@^3.3.4 axios@^1.5.0
```

## 📝 **API 엔드포인트**

### 기본 API
- `GET /api/menu` - 메뉴 데이터 조회
- `POST /api/orders/{customer_name}/items` - 주문 생성/추가
- `GET /api/orders/{customer_name}` - 고객별 주문 내역 조회
- `DELETE /api/orders/{customer_name}` - 고객별 주문 삭제
- `GET /api/orders` - 전체 주문 내역 조회 (관리자용)

### 새로운 API (SQLite 버전)
- `GET /api/test` - 서버 연결 테스트
- `GET /api/stats` - 주문 통계 조회

### **접속 주소**
- **키오스크**: http://localhost:5173
- **API 문서**: http://localhost:8000/docs  
- **주문 내역**: http://localhost:8000/api/orders
- **통계**: http://localhost:8000/api/stats

## 🐛 **문제 해결 (SQLite 버전)**

### **업그레이드 관련 문제**

#### **의존성 설치 오류**
```bash
cd back
pip install -r requirements.txt
# 또는
./setup_sqlite.sh  # 자동 설치
```

#### **데이터베이스 초기화**
```bash
cd back
python db_manager.py
# 5번 선택: 데이터베이스 완전 초기화
```

### **여러 사용자 동시 접속 테스트**
1. **다른 브라우저/시크릿 모드**로 동시 접속
2. **다른 사람이 동시에** 주문 진행
3. **데이터 충돌 없이** 모든 주문이 저장되는지 확인

### **기존 문제 해결**

#### **백엔드 연결 테스트**
```bash
curl http://localhost:8000/api/test
# 예상 응답: {"status":"ok","message":"...상태: SQLite 버전..."}
```

#### **데이터베이스 상태 확인**
```bash
cd back
python db_manager.py
# 1번 선택: 데이터베이스 상태 확인
```

#### **데이터 백업**
```bash
cd back
python db_manager.py
# 3번 선택: JSON으로 데이터 내보내기
```

### **일반적인 해결 방법**
1. **서버 재시작**
   ```bash
   cd back && python app.py
   cd front && npm run dev
   ```

2. **캐시 삭제**
   - 브라우저: Ctrl+Shift+R
   - Node.js: `rm -rf front/node_modules && npm install`

3. **포트 충돌 해결**
   ```bash
   lsof -i :8000  # 8000번 포트 사용 현황 확인
   ```

### **성능 벤치마크**
- **단일 사용자**: 즉시 주문 완료
- **10명 동시 주문**: 모든 주문 안전하게 저장
- **100명+ 동시 주문**: PostgreSQL 등으로 업그레이드 권장

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
