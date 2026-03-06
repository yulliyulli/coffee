import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'

// 개발 환경에서는 localhost, 프로덕션에서는 상대 경로 사용
if (import.meta.env.DEV) {
  axios.defaults.baseURL = 'http://localhost:8000'
}

// ngrok 경고 페이지 우회 헤더
axios.defaults.headers.common['ngrok-skip-browser-warning'] = 'true'

createApp(App).use(router).mount('#app')