<!-- KioskView.vue -->
<template>
  <div class="kiosk-container">
    <header class="header">
      <h1>☕ 카페 주문 키오스크</h1>
      <button @click="goToAdmin" class="admin-btn">관리자</button>
    </header>

    <!-- 1. 사용자 이름 입력 -->
    <div v-if="currentStep === 'name'" class="step-container">
      <h2>주문하실 분의 성함을 입력해주세요</h2>
      <input
        v-model="customerName"
        placeholder="이름을 입력하세요"
        class="name-input"
        @keyup.enter="checkExistingOrder"
      />
      <button @click="checkExistingOrder" :disabled="!customerName" class="next-btn">
        다음
      </button>
      
      <!-- 로딩 표시 -->
      <div v-if="loading" class="loading">
        확인 중...
      </div>
    </div>

    <!-- 2. 기존 주문 내역 표시 -->
    <div v-if="currentStep === 'existing-order'" class="step-container">
      <h2>{{ customerName }}님의 기존 주문 내역</h2>
      
      <div class="existing-orders">
        <div v-for="order in existingOrders" :key="order.order_id" class="order-summary">
          <h3>주문번호: {{ order.order_id }}</h3>
          <div class="order-time">주문시간: {{ formatDate(order.timestamp) }}</div>
          
          <div class="order-items-list">
            <div v-for="(item, index) in order.items" :key="index" class="order-item-summary">
              <strong>{{ item.name }}</strong>
              <div class="item-options">
                <span v-for="(value, key) in item.options" :key="key" class="option-tag">
                  {{ key }}: {{ value }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="action-buttons">
        <button @click="deleteExistingOrders" class="delete-btn">
          기존 주문 삭제하고 새로 주문
        </button>
        <button @click="currentStep = 'name'" class="back-btn">이전</button>
      </div>
    </div>

    <!-- 3. 카테고리 및 음료 선택 -->
    <div v-if="currentStep === 'menu'" class="step-container">
      <h2>{{ customerName }}님, 음료를 선택해주세요</h2>

      <!-- 카테고리 탭 -->
      <div class="category-tabs">
        <button
          v-for="category in menu.categories"
          :key="category.name"
          @click="selectedCategory = category.name"
          :class="{ active: selectedCategory === category.name }"
          class="category-tab"
        >
          {{ category.name }}
        </button>
      </div>

      <!-- 음료 리스트 -->
      <div class="drinks-grid">
        <div
          v-for="item in currentCategoryItems"
          :key="item.name"
          @click="selectDrink(item)"
          class="drink-item"
        >
          <h3>{{ item.name }}</h3>
        </div>
      </div>

      <div class="action-buttons">
        <button @click="goBack" class="back-btn">이전</button>
      </div>
    </div>

    <!-- 4. 옵션 선택 -->
    <div v-if="currentStep === 'options'" class="step-container">
      <h2>{{ selectedDrink.name }} 옵션을 선택해주세요</h2>

      <div v-for="(optionValues, optionName) in selectedDrink.options" :key="optionName" class="option-group">
        <h3>{{ optionName }}</h3>
        <div class="option-buttons">
          <button
            v-for="value in optionValues"
            :key="value"
            @click="selectOption(optionName, value)"
            :class="{ active: selectedOptions[optionName] === value }"
            class="option-btn"
          >
            {{ value }}
          </button>
        </div>
      </div>

      <div class="action-buttons">
        <button @click="currentStep = 'menu'" class="back-btn">이전</button>
        <button @click="confirmOrder" class="confirm-btn">주문 확인</button>
      </div>
    </div>

    <!-- 5. 주문 확인 및 완료 -->
    <div v-if="currentStep === 'order'" class="step-container">
      <h2>{{ customerName }}님의 주문 확인</h2>

      <div class="final-order-summary">
        <div class="order-item-final">
          <h3>{{ selectedDrink.name }}</h3>
          <div class="order-options">
            <span v-for="(value, key) in selectedOptions" :key="key" class="option-tag">
              {{ key }}: {{ value }}
            </span>
          </div>
        </div>
      </div>

      <div class="order-confirmation">
        <p><strong>{{ customerName }}</strong>님의 주문이 맞습니까?</p>
        <p class="drink-name">{{ selectedDrink.name }}</p>
        <div class="options-summary">
          <div v-for="(value, key) in selectedOptions" :key="key" class="option-line">
            <span class="option-key">{{ key }}:</span>
            <span class="option-value">{{ value }}</span>
          </div>
        </div>
      </div>

      <div class="action-buttons">
        <button @click="currentStep = 'options'" class="back-btn">이전</button>
        <button 
          @click="submitOrder" 
          :disabled="submitting"
          class="submit-btn"
        >
          {{ submitting ? '주문 중...' : '주문 완료' }}
        </button>
      </div>
    </div>

    <!-- 6. 주문 완료 -->
    <div v-if="currentStep === 'complete'" class="step-container">
      <h2>주문이 완료되었습니다! 🎉</h2>
      <div class="completion-info">
        <p><strong>{{ customerName }}</strong>님</p>
        <p class="drink-ordered">{{ completedOrder.name }}</p>
        <div class="completed-options">
          <span v-for="(value, key) in completedOrder.options" :key="key" class="option-tag">
            {{ key }}: {{ value }}
          </span>
        </div>
        <p class="order-id">주문번호: <strong>{{ orderId }}</strong></p>
        <p class="thank-you">맛있게 드세요! ☕</p>
      </div>
      <button @click="resetOrder" class="reset-btn">새 주문 시작</button>
    </div>

    <!-- 에러 메시지 -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
      <button @click="errorMessage = ''" class="close-error">×</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'KioskView',
  data() {
    return {
      currentStep: 'name', // name, existing-order, menu, options, order, complete
      customerName: '',
      menu: { categories: [] },
      selectedCategory: '',
      selectedDrink: null,
      selectedOptions: {},
      existingOrders: [],
      completedOrder: {},
      orderId: null,
      loading: false,
      submitting: false,
      errorMessage: ''
    }
  },
  computed: {
    currentCategoryItems() {
      const category = this.menu.categories.find(c => c.name === this.selectedCategory)
      return category ? category.items : []
    }
  },
  async mounted() {
    await this.loadMenu()
  },
  methods: {
    async loadMenu() {
      try {
        console.log('메뉴 로드 시도 중...')
        const response = await axios.get('/api/menu')
        this.menu = response.data
        
        if (this.menu && this.menu.categories && this.menu.categories.length > 0) {
          this.selectedCategory = this.menu.categories[0].name
          console.log('메뉴 로드 성공:', this.menu.categories.length, '개 카테고리')
        } else {
          console.error('메뉴 데이터가 비어있습니다.')
          this.showError('메뉴 데이터가 비어있습니다. 관리자에게 문의해주세요.')
        }
      } catch (error) {
        console.error('메뉴 로드 실패:', error)
        if (error.response) {
          this.showError(`서버 오류: 메뉴를 불러올 수 없습니다. (상태: ${error.response.status})`)
        } else if (error.request) {
          this.showError('서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해주세요.')
        } else {
          this.showError('메뉴를 불러오는 중 오류가 발생했습니다. 새로고침 후 다시 시도해주세요.')
        }
      }
    },

    async checkExistingOrder() {
      if (!this.customerName.trim()) return
      
      this.loading = true
      this.errorMessage = '' // 에러 메시지 초기화
      
      try {
        const response = await axios.get(`/api/orders/${this.customerName}`)
        
        // API 응답 구조 처리 (orders 배열로 처리)
        const orderData = response.data
        this.existingOrders = orderData.orders || orderData || []
        
        console.log('주문 내역 확인:', this.existingOrders)
        
        if (this.existingOrders.length > 0) {
          // 기존 주문이 있으면 표시
          this.currentStep = 'existing-order'
        } else {
          // 기존 주문이 없으면 바로 메뉴로
          this.currentStep = 'menu'
        }
      } catch (error) {
        console.error('주문 내역 확인 에러:', error)
        
        // 네트워크 에러가 아닌 경우 (404, 500 등) 메뉴로 이동
        if (error.response && error.response.status) {
          console.log('서버 응답 에러, 메뉴로 이동')
          this.currentStep = 'menu'
        } else {
          // 네트워크 에러인 경우만 에러 메시지 표시
          this.showError('네트워크 연결에 문제가 있습니다. 다시 시도해주세요.')
        }
      } finally {
        this.loading = false
      }
    },

    async deleteExistingOrders() {
      try {
        const response = await axios.delete(`/api/orders/${this.customerName}`)
        if (response.data.status === 'success') {
          this.existingOrders = []
          this.currentStep = 'menu'
        }
      } catch (error) {
        console.error('주문 삭제 실패:', error)
        if (error.response && error.response.status === 404) {
          // 삭제할 주문이 없는 경우도 메뉴로 이동
          this.existingOrders = []
          this.currentStep = 'menu'
        } else {
          this.showError('주문 삭제에 실패했습니다.')
        }
      }
    },

    goBack() {
      if (this.existingOrders.length > 0) {
        this.currentStep = 'existing-order'
      } else {
        this.currentStep = 'name'
      }
    },

    selectDrink(drink) {
      this.selectedDrink = drink
      this.selectedOptions = {}
      this.currentStep = 'options'
    },

    selectOption(optionName, value) {
      this.selectedOptions[optionName] = value
    },

    confirmOrder() {
      // 옵션이 모두 선택되었는지 확인 (선택사항)
      const requiredOptions = Object.keys(this.selectedDrink.options)
      const selectedOptionKeys = Object.keys(this.selectedOptions)
      
      if (requiredOptions.length > selectedOptionKeys.length) {
        this.showError('모든 옵션을 선택해주세요.')
        return
      }
      
      // 바로 주문 확인 페이지로 이동
      this.currentStep = 'order'
    },

    async submitOrder() {
      if (!this.selectedDrink || !this.customerName) {
        this.showError('주문할 음료를 선택해주세요.')
        return
      }

      this.submitting = true
      try {
        // 주문 데이터 구성
        const orderItem = {
          name: this.selectedDrink.name,
          options: { ...this.selectedOptions }
        }

        console.log('주문 데이터:', orderItem)

        // API 호출
        const response = await axios.post(`/api/orders/${this.customerName}/items`, orderItem)
        
        console.log('주문 응답:', response.data)
        
        if (response.data.status === 'success') {
          // 성공 시 완료된 주문 정보 저장
          this.completedOrder = orderItem
          this.orderId = new Date().toISOString().replace(/[-:]/g, '').split('.')[0]
          this.currentStep = 'complete'
        } else {
          this.showError('주문 처리에 실패했습니다.')
        }
      } catch (error) {
        console.error('주문 제출 실패:', error)
        if (error.response) {
          this.showError(`주문 제출 실패: ${error.response.status} - ${error.response.data?.message || '서버 오류'}`)
        } else if (error.request) {
          this.showError('서버에 연결할 수 없습니다. 네트워크를 확인해주세요.')
        } else {
          this.showError('주문 제출 중 오류가 발생했습니다. 다시 시도해주세요.')
        }
      } finally {
        this.submitting = false
      }
    },

    resetOrder() {
      this.currentStep = 'name'
      this.customerName = ''
      this.selectedDrink = null
      this.selectedOptions = {}
      this.existingOrders = []
      this.completedOrder = {}
      this.orderId = null
      this.errorMessage = ''
    },

    goToAdmin() {
      this.$router.push('/admin')
    },

    showError(message) {
      this.errorMessage = message
      setTimeout(() => {
        this.errorMessage = ''
      }, 5000)
    },

    formatDate(dateString) {
      if (!dateString) return ''
      return new Date(dateString).toLocaleString('ko-KR')
    }
  }
}
</script>

<style scoped>
.kiosk-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Noto Sans KR', sans-serif;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.header {
  text-align: center;
  margin-bottom: 30px;
  background: white;
  padding: 20px;
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h1 {
  color: #2c3e50;
  margin: 0;
  font-size: 2.2em;
}

.admin-btn {
  background: #dc3545;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.admin-btn:hover {
  background: #c82333;
  transform: translateY(-1px);
}

.step-container {
  background: white;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  text-align: center;
}

.step-container h2 {
  color: #2c3e50;
  margin-bottom: 25px;
  font-size: 1.5em;
}

.name-input {
  padding: 15px 20px;
  font-size: 18px;
  margin: 20px;
  border: 2px solid #e0e6ed;
  border-radius: 10px;
  width: 300px;
  transition: border-color 0.3s;
}

.name-input:focus {
  outline: none;
  border-color: #007bff;
}

.loading {
  margin-top: 15px;
  color: #6c757d;
  font-style: italic;
}

.existing-orders {
  max-width: 600px;
  margin: 0 auto;
}

.order-summary {
  background: #f8f9fa;
  padding: 20px;
  margin: 15px 0;
  border-radius: 10px;
  border-left: 4px solid #007bff;
}

.order-time {
  color: #6c757d;
  font-size: 0.9em;
  margin-bottom: 15px;
}

.order-items-list {
  text-align: left;
}

.order-item-summary {
  margin: 10px 0;
  padding: 10px;
  background: white;
  border-radius: 8px;
}

.category-tabs {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  margin: 20px 0;
  gap: 10px;
}

.category-tab {
  padding: 12px 20px;
  border: 2px solid #e0e6ed;
  background: white;
  cursor: pointer;
  border-radius: 25px;
  transition: all 0.3s;
  font-weight: 500;
  font-size: 16px;
}

.category-tab:hover {
  border-color: #007bff;
  background: #f8f9fa;
}

.category-tab.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.drinks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin: 25px 0;
}

.drink-item {
  padding: 20px;
  border: 2px solid #e0e6ed;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
}

.drink-item:hover {
  background: #f8f9fa;
  border-color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0,123,255,0.2);
}

.option-group {
  margin: 25px 0;
  text-align: left;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.option-group h3 {
  margin-bottom: 15px;
  color: #2c3e50;
  font-size: 1.1em;
}

.option-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.option-btn {
  padding: 10px 15px;
  border: 2px solid #e0e6ed;
  background: white;
  cursor: pointer;
  border-radius: 20px;
  transition: all 0.3s;
  font-size: 0.9em;
}

.option-btn:hover {
  border-color: #28a745;
  background: #f8f9fa;
}

.option-btn.active {
  background: #28a745;
  color: white;
  border-color: #28a745;
}

/* 주문 확인 페이지 스타일 */
.final-order-summary {
  max-width: 500px;
  margin: 20px auto;
  background: #f8f9fa;
  padding: 25px;
  border-radius: 12px;
  border: 2px solid #e9ecef;
}

.order-item-final {
  text-align: left;
}

.order-item-final h3 {
  color: #2c3e50;
  margin-bottom: 15px;
  font-size: 1.3em;
  text-align: center;
}

.order-confirmation {
  margin: 25px 0;
  padding: 20px;
  background: #e8f4fd;
  border-radius: 10px;
  border-left: 4px solid #007bff;
}

.drink-name {
  font-size: 1.2em;
  font-weight: bold;
  color: #2c3e50;
  margin: 10px 0;
}

.options-summary {
  margin-top: 15px;
}

.option-line {
  display: flex;
  justify-content: space-between;
  margin: 8px 0;
  padding: 5px 0;
  border-bottom: 1px solid rgba(0,0,0,0.1);
}

.option-key {
  font-weight: 500;
  color: #6c757d;
}

.option-value {
  font-weight: 600;
  color: #2c3e50;
}

.action-buttons {
  margin-top: 30px;
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
}

/* 버튼 스타일 개선 - 텍스트 크기 확대 */
.next-btn, .confirm-btn, .submit-btn {
  background: #007bff;
  color: white;
  padding: 18px 35px;
  border: none;
  border-radius: 10px;
  font-size: 18px; /* 크기 증가 */
  font-weight: 600; /* 굵기 증가 */
  cursor: pointer;
  transition: all 0.3s;
  min-width: 140px;
}

.next-btn:hover, .confirm-btn:hover, .submit-btn:hover {
  background: #0056b3;
  transform: translateY(-2px);
}

.next-btn:disabled, .submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

.back-btn {
  background: #6c757d;
  color: white;
  padding: 15px 30px; /* 크기 증가 */
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 16px; /* 크기 증가 */
  font-weight: 500; /* 굵기 증가 */
  min-width: 120px;
}

.back-btn:hover {
  background: #545b62;
}

.delete-btn {
  background: #dc3545;
  color: white;
  padding: 15px 30px; /* 크기 증가 */
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 16px; /* 크기 증가 */
  font-weight: 500; /* 굵기 증가 */
}

.delete-btn:hover {
  background: #c82333;
}

.option-tag {
  background: #e9ecef;
  padding: 6px 12px;
  margin: 3px;
  border-radius: 15px;
  display: inline-block;
  font-size: 0.9em;
  color: #495057;
}

.completion-info {
  background: #d4edda;
  padding: 30px;
  border-radius: 15px;
  margin: 20px 0;
  color: #155724;
}

.completion-info p {
  margin: 10px 0;
  font-size: 1.1em;
}

.drink-ordered {
  font-size: 1.3em !important;
  font-weight: bold !important;
  color: #0f5132 !important;
  margin: 15px 0 !important;
}

.completed-options {
  margin: 15px 0;
}

.order-id {
  font-size: 1.2em !important;
  font-weight: bold !important;
}

.thank-you {
  font-size: 1.4em !important;
  font-weight: bold !important;
  margin-top: 20px !important;
}

.reset-btn {
  background: #28a745;
  color: white;
  padding: 18px 35px;
  border: none;
  border-radius: 10px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.reset-btn:hover {
  background: #218838;
}

.error-message {
  position: fixed;
  top: 20px;
  right: 20px;
  background: #f8d7da;
  color: #721c24;
  padding: 15px 20px;
  border-radius: 8px;
  border: 1px solid #f5c6cb;
  max-width: 400px;
  z-index: 1000;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
  font-weight: 500;
}

.close-error {
  background: none;
  border: none;
  color: #721c24;
  font-size: 20px;
  cursor: pointer;
  float: right;
  margin-left: 10px;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .kiosk-container {
    padding: 10px;
  }
  
  .header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .header h1 {
    font-size: 1.8em;
  }
  
  .name-input {
    width: 100%;
    max-width: 300px;
  }
  
  .drinks-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .action-buttons button {
    width: 100%;
    max-width: 300px;
    margin: 5px 0;
  }
  
  .option-line {
    flex-direction: column;
    gap: 5px;
  }
}
</style>
