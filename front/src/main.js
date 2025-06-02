import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'

// Axios 기본 설정 (FastAPI 기본 포트 8000으로 변경)
axios.defaults.baseURL = 'http://localhost:8000'
axios.defaults.headers.common['Content-Type'] = 'application/json'

// CORS 설정
axios.defaults.withCredentials = false

// 요청 인터셉터 (로딩 표시 등에 사용 가능)
axios.interceptors.request.use(
  config => {
    console.log('API 요청:', config.method?.toUpperCase(), config.url)
    return config
  },
  error => {
    console.error('요청 오류:', error)
    return Promise.reject(error)
  }
)

// 응답 인터셉터 (에러 처리)
axios.interceptors.response.use(
  response => {
    console.log('API 응답:', response.status, response.config.url)
    return response
  },
  error => {
    console.error('응답 오류:', error.response?.status, error.config?.url)

    // 네트워크 오류 처리
    if (!error.response) {
      console.error('네트워크 오류: 백엔드 서버가 실행되지 않았을 수 있습니다.')
    }

    return Promise.reject(error)
  }
)

const app = createApp(App)

// Router 사용
app.use(router)

// Axios를 전역 속성으로 등록
app.config.globalProperties.$http = axios

// 전역 속성 추가
app.config.globalProperties.$formatPrice = (price) => {
  return price?.toLocaleString() || '0'
}

app.config.globalProperties.$formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('ko-KR')
}

// 에러 핸들러
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue 에러:', err, info)
}

app.mount('#app')