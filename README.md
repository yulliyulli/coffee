# ☕ 커피 주문 시스템

Vue.js + Python FastAPI + SQLite로 구현한 커피 주문 키오스크 시스템입니다.

## ✨ 주요 기능

### 키오스크 (주문 화면)
- 이름 입력 후 메뉴 선택
- 카테고리별 메뉴 탐색
- 옵션 선택 (온도, 사이즈 등)
- 주문 확인 및 완료

### 관리자 화면
- **주문함 관리**: 여러 주문함 생성/관리 (예: "3월 5일 오후 주문")
- **카페 선택**: 파란만잔, 텐퍼센트 등 카페별 메뉴 지원
- **1인 1메뉴 제한**: 주문함별 한 사람당 하나의 메뉴만 주문 가능 설정
- **주문 현황**: 메뉴별 수량, 고객별 주문, 전체 주문 내역 조회
- **주문 수동 추가**: 관리자가 직접 주문 입력
- **텍스트 다운로드**: 주문 요약 텍스트 파일 생성

## 🛠 기술 스택

| 구분 | 기술 |
|------|------|
| 백엔드 | Python FastAPI, SQLAlchemy, SQLite |
| 프론트엔드 | Vue.js 3, Axios, Vite |
| 외부 접근 | ngrok |

## 📁 프로젝트 구조

```
coffee/
├── back/                       # 백엔드
│   ├── app.py                  # FastAPI 서버
│   ├── database.py             # DB 모델
│   ├── config/
│   │   └── menus/              # 카페별 메뉴
│   │       ├── 파란만잔.yml
│   │       └── 텐퍼센트.yml
│   └── data/
│       └── coffee_orders.db    # SQLite DB
├── front/                      # 프론트엔드
│   ├── src/
│   │   ├── views/
│   │   │   └── KioskView.vue   # 키오스크 화면
│   │   ├── components/
│   │   │   └── AdminPanel.vue  # 관리자 화면
│   │   └── router/
│   │       └── index.js        # 라우팅
│   ├── dist/                   # 빌드 결과물
│   └── public/
│       └── images/menu/        # 메뉴 이미지
└── README.md
```

## 🚀 실행 방법

### 1. 백엔드 실행

```bash
cd back
source .venv/bin/activate   # 가상환경 활성화
pip install -r requirements.txt
python app.py
```

### 2. 프론트엔드 실행 (개발 모드)

```bash
cd front
npm install
npm run dev
```

### 3. 접속

| 화면 | 주소 |
|------|------|
| 키오스크 | http://localhost:5173 |
| 관리자 | http://localhost:5173/admin |

## 🌐 외부 접근 (모바일 등)

### 같은 Wi-Fi 네트워크에서

1. 프론트엔드 빌드:
```bash
cd front
npm run build
```

2. 백엔드만 실행하면 프론트엔드도 함께 서빙됩니다:
```bash
cd back
python app.py
```

3. 접속: `http://{컴퓨터IP}:8000`

### 외부 인터넷에서 (ngrok)

1. ngrok 설치 및 인증:
```bash
brew install ngrok
ngrok config add-authtoken YOUR_TOKEN
```

2. 터널 실행:
```bash
ngrok http 8000
```

3. 생성된 URL로 접속

## 📊 주문함 기능

### 주문함 생성
1. 관리자 화면 접속
2. "새 주문함" 클릭
3. 이름 입력 (예: "3월 5일 오후 주문")
4. 카페 선택
5. 1인 1메뉴 제한 여부 설정

### 1인 1메뉴 제한
- 체크 시: 한 사람당 하나의 메뉴만 주문 가능
- 이미 주문한 사람은 이름 입력 시 알림

## 🔧 메뉴 설정

`back/config/menus/{카페명}.yml` 파일에서 관리:

```yaml
categories:
  - name: "커피"
    items:
      - name: "아메리카노"
        image: "/images/menu/americano.png"
        options:
          temperature: ["HOT", "ICE"]
```

## 📝 API 엔드포인트

### 주문함
- `GET /api/carts` - 주문함 목록
- `GET /api/carts/active` - 활성 주문함
- `POST /api/carts` - 주문함 생성
- `PUT /api/carts/{id}/activate` - 주문함 활성화
- `DELETE /api/carts/{id}` - 주문함 삭제

### 주문
- `GET /api/menu` - 메뉴 조회
- `POST /api/orders/{customer_name}/items` - 주문 추가
- `GET /api/orders/{customer_name}` - 고객별 주문 조회
- `GET /api/admin/orders` - 관리자용 전체 주문

## 🐛 문제 해결

### "메뉴를 불러올 수 없습니다"
- 백엔드가 실행 중인지 확인
- 외부 접근 시 프론트엔드 빌드 후 백엔드에서 서빙

### 동시 주문 문제
- SQLite 트랜잭션으로 동시성 지원
- 1인 1메뉴 제한 시 중복 체크

### ngrok "Visit Site" 페이지
- 무료 버전 제한사항
- 첫 접속 시 "Visit Site" 클릭 필요

## 📄 라이선스

MIT License
