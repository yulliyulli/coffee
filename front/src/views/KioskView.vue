<template>
  <div class="kiosk">
    <!-- 헤더 -->
    <header class="header">
      <div class="header-title">
        <h1 v-if="cartName">{{ cartName }}</h1>
        <h1 v-else>☕ 커피 주문</h1>
        <span v-if="cafeName" class="cafe-tag">{{ cafeName }}</span>
      </div>
      <div class="header-right">
        <span v-if="customerName && step > 1" class="customer-badge">{{ customerName }}님</span>
      </div>
    </header>

    <!-- STEP 1: 이름 입력 -->
    <main v-if="step === 1" class="content name-step">
      <div class="name-card">
        <div class="name-icon">☕</div>
        <h2>반갑습니다!</h2>
        <p class="name-description">주문을 위해 이름을 입력해주세요</p>
        <input
          v-model="customerName"
          type="text"
          placeholder="이름"
          class="name-input"
          @keyup.enter="goToMenu"
        />
        <button
          class="btn-primary btn-next"
          :disabled="!customerName.trim()"
          @click="goToMenu"
        >
          다음
        </button>
      </div>
    </main>

    <!-- STEP 2: 메뉴 선택 -->
    <main v-if="step === 2" class="content">
      <!-- 카테고리 탭 -->
      <div class="category-tabs">
        <button
          v-for="cat in menu.categories"
          :key="cat.name"
          :class="['tab', { active: selectedCategory === cat.name }]"
          @click="selectedCategory = cat.name"
        >
          {{ cat.name }}
        </button>
      </div>

      <!-- 음료 그리드 -->
      <div class="menu-grid">
        <button
          v-for="item in currentItems"
          :key="item.name"
          class="menu-item"
          @click="selectDrink(item)"
        >
          <img v-if="item.image" :src="item.image" :alt="item.name" class="menu-image" />
          <span class="menu-name">{{ item.name }}</span>
        </button>
      </div>
    </main>

    <!-- STEP 3: 옵션 선택 -->
    <main v-if="step === 3" class="content">
      <h2 class="drink-title">{{ selectedDrink.name }}</h2>

      <div v-for="(values, key) in selectedDrink.options" :key="key" class="option-group">
        <label class="option-label">{{ getOptionLabel(key) }}</label>
        <div class="option-buttons">
          <button
            v-for="val in values"
            :key="val"
            :class="['option-btn', { active: selectedOptions[key] === val }]"
            @click="selectedOptions[key] = val"
          >
            {{ val }}
          </button>
        </div>
      </div>

      <div class="actions">
        <button class="btn-back" @click="step = 2">이전</button>
        <button
          class="btn-primary"
          :disabled="!isOptionsComplete"
          @click="showConfirm"
        >
          주문하기
        </button>
      </div>
    </main>

    <!-- STEP 4: 완료 -->
    <main v-if="step === 4" class="content complete">
      <div class="complete-icon">✓</div>
      <h2>주문이 완료되었습니다</h2>
    </main>

    <!-- 확인 모달 -->
    <div v-if="showConfirmModal" class="modal-overlay" @click.self="showConfirmModal = false">
      <div class="modal">
        <p class="modal-text">
          <strong>{{ orderSummary }}</strong>
          <br />주문하시겠습니까?
        </p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showConfirmModal = false">취소</button>
          <button class="btn-confirm" @click="submitOrder">주문</button>
        </div>
      </div>
    </div>

    <!-- 에러 토스트 -->
    <div v-if="error" class="toast">{{ error }}</div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      step: 1,
      customerName: '',
      cartName: '',
      cafeName: '',
      singleOrder: false,
      menu: { categories: [] },
      selectedCategory: '',
      selectedDrink: null,
      selectedOptions: {},
      showConfirmModal: false,
      error: ''
    }
  },
  computed: {
    currentItems() {
      const cat = this.menu.categories.find(c => c.name === this.selectedCategory)
      return cat ? cat.items : []
    },
    isOptionsComplete() {
      if (!this.selectedDrink?.options) return true
      return Object.keys(this.selectedDrink.options).every(key => this.selectedOptions[key])
    },
    orderSummary() {
      if (!this.selectedDrink) return ''
      const optionValues = Object.values(this.selectedOptions)
      if (optionValues.length === 0) {
        return this.selectedDrink.name
      }
      return `${this.selectedDrink.name} (${optionValues.join(', ')})`
    }
  },
  async mounted() {
    await this.loadActiveCart()
    await this.loadMenu()
  },
  methods: {
    async loadActiveCart() {
      try {
        const { data } = await axios.get('/api/carts/active')
        if (data.cart) {
          this.cartName = data.cart.name
          this.cafeName = data.cart.cafe
          this.singleOrder = data.cart.single_order || false
        }
      } catch (e) {
        console.error('활성 주문함 로드 실패:', e)
      }
    },
    async loadMenu() {
      try {
        const cafe = this.cafeName || '파란만잔'
        const { data } = await axios.get(`/api/menu?cafe=${encodeURIComponent(cafe)}`)
        this.menu = data
        if (data.categories?.length) {
          this.selectedCategory = data.categories[0].name
        }
      } catch (e) {
        this.showError('메뉴를 불러올 수 없습니다')
      }
    },
    async goToMenu() {
      if (!this.customerName.trim()) {
        this.showError('이름을 입력해주세요')
        return
      }

      // 1인 1메뉴 제한 체크
      if (this.singleOrder) {
        try {
          const { data } = await axios.get(`/api/orders/${this.customerName}`)
          if (data.count > 0) {
            this.showError(`${this.customerName}님은 이미 주문하셨습니다`)
            return
          }
        } catch (e) {
          console.error('주문 확인 실패:', e)
        }
      }

      this.step = 2
    },
    selectDrink(item) {
      this.selectedDrink = item
      this.selectedOptions = {}
      // 옵션이 없으면 바로 확인 모달
      if (!item.options || Object.keys(item.options).length === 0) {
        this.showConfirm()
      } else {
        this.step = 3
      }
    },
    getOptionLabel(key) {
      const labels = {
        size: '사이즈',
        temperature: '온도',
        milk: '우유',
        shot: '샷',
        syrup: '시럽',
        whip: '휘핑',
        ice: '얼음',
        sweetness: '당도',
        base: '베이스',
        sweetener: '감미료',
        lemon: '레몬'
      }
      return labels[key] || key
    },
    showConfirm() {
      this.showConfirmModal = true
    },
    async submitOrder() {
      try {
        const order = {
          name: this.selectedDrink.name,
          options: { ...this.selectedOptions }
        }
        await axios.post(`/api/orders/${this.customerName}/items`, order)
        this.showConfirmModal = false
        this.step = 4
        // 7초 후 자동으로 처음 화면으로
        setTimeout(() => {
          this.reset()
        }, 7000)
      } catch (e) {
        this.showConfirmModal = false
        const errorMsg = e.response?.data?.detail || '주문에 실패했습니다'
        this.showError(errorMsg)
      }
    },
    reset() {
      this.step = 1
      this.customerName = ''
      this.selectedDrink = null
      this.selectedOptions = {}
    },
    showError(msg) {
      this.error = msg
      setTimeout(() => this.error = '', 3000)
    }
  }
}
</script>

<style scoped>
/*
 * Latte Cream Palette
 * Pure Cream: #FFFBF5 - main background
 * Latte Foam: #F5F0EA - secondary background
 * Warm Milk: #E8E0D8 - borders, dividers
 * Caramel: #C8A67E - primary accent, buttons
 * Mocha: #8B7355 - secondary text
 * Espresso: #5D4E42 - primary text
 * Dark Roast: #3A3330 - headers, dark elements
 */

.kiosk {
  max-width: 480px;
  margin: 0 auto;
  min-height: 100vh;
  background: #FFFBF5;
  display: flex;
  flex-direction: column;
}

.header {
  background: #C8A67E;
  color: #3A3330;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.header h1 {
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0;
  color: #3A3330;
}

.cafe-tag {
  background: rgba(255, 251, 245, 0.85);
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
  color: #5D4E42;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.customer-badge {
  background: rgba(255, 251, 245, 0.9);
  color: #5D4E42;
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
}

.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

/* Step 1: 이름 입력 */
.name-step {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #F5F0EA;
}

.name-card {
  width: 100%;
  max-width: 320px;
  text-align: center;
  padding: 48px 28px;
  background: #fff;
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(58, 51, 48, 0.08);
}

.name-icon {
  width: 80px;
  height: 80px;
  background: #F5F0EA;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  margin: 0 auto 20px;
}

.name-card h2 {
  font-size: 1.8rem;
  margin-bottom: 8px;
  color: #3A3330;
  font-weight: 700;
}

.name-description {
  color: #8B7355;
  margin-bottom: 32px;
  font-size: 1rem;
  line-height: 1.5;
}

.name-input {
  width: 100%;
  padding: 16px;
  font-size: 1.2rem;
  border: 2px solid #E8E0D8;
  border-radius: 12px;
  outline: none;
  transition: all 0.2s;
  box-sizing: border-box;
  text-align: center;
  margin-bottom: 20px;
  background: #FFFBF5;
}

.name-input:focus {
  border-color: #C8A67E;
  background: #fff;
  box-shadow: 0 0 0 4px rgba(200, 166, 126, 0.15);
}

.btn-next {
  width: 100%;
  padding: 18px;
  font-size: 1.2rem;
}

/* Step 2: 메뉴 선택 */
.category-tabs {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 16px;
  margin-bottom: 16px;
}

.tab {
  flex-shrink: 0;
  padding: 12px 20px;
  border: none;
  background: #F5F0EA;
  border-radius: 25px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  color: #5D4E42;
}

.tab.active {
  background: #3A3330;
  color: #FFFBF5;
}

.menu-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.menu-item {
  padding: 12px;
  border: 1px solid #E8E0D8;
  border-radius: 12px;
  background: #fff;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #3A3330;
}

.menu-item:hover {
  border-color: #C8A67E;
  background: #FFFBF5;
}

.menu-item:active {
  transform: scale(0.98);
}

.menu-image {
  width: 80px;
  height: 80px;
  object-fit: contain;
  border-radius: 8px;
}

.menu-name {
  text-align: center;
  line-height: 1.3;
}

/* Step 3: 옵션 선택 */
.drink-title {
  text-align: center;
  font-size: 1.5rem;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #E8E0D8;
  color: #3A3330;
}

.option-group {
  margin-bottom: 24px;
}

.option-label {
  display: block;
  font-weight: 600;
  margin-bottom: 12px;
  color: #5D4E42;
}

.option-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.option-btn {
  padding: 12px 16px;
  border: 1px solid #E8E0D8;
  border-radius: 8px;
  background: #fff;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  color: #5D4E42;
}

.option-btn.active {
  border-color: #3A3330;
  background: #3A3330;
  color: #FFFBF5;
}

.actions {
  display: flex;
  gap: 12px;
  margin-top: 32px;
  padding-top: 20px;
  border-top: 1px solid #E8E0D8;
}

.btn-back {
  flex: 1;
  padding: 16px;
  border: 1px solid #E8E0D8;
  border-radius: 12px;
  background: #fff;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  color: #5D4E42;
}

.btn-primary {
  flex: 2;
  padding: 16px;
  border: none;
  border-radius: 12px;
  background: #C8A67E;
  color: #fff;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: #b8966e;
}

.btn-primary:disabled {
  background: #E8E0D8;
  color: #8B7355;
  cursor: not-allowed;
}

/* Step 4: 완료 */
.complete {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.complete-icon {
  width: 80px;
  height: 80px;
  background: #C8A67E;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  margin-bottom: 24px;
}

.complete h2 {
  font-size: 1.5rem;
  margin-bottom: 16px;
  color: #3A3330;
}

/* 확인 모달 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(58, 51, 48, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 20px;
}

.modal {
  background: #fff;
  border-radius: 16px;
  padding: 32px 24px;
  max-width: 320px;
  width: 100%;
  text-align: center;
}

.modal-text {
  font-size: 1.1rem;
  line-height: 1.6;
  margin-bottom: 24px;
  color: #3A3330;
}

.modal-text strong {
  font-size: 1.2rem;
  color: #3A3330;
}

.modal-actions {
  display: flex;
  gap: 12px;
}

.btn-cancel {
  flex: 1;
  padding: 14px;
  border: 1px solid #E8E0D8;
  border-radius: 10px;
  background: #fff;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  color: #5D4E42;
}

.btn-confirm {
  flex: 1;
  padding: 14px;
  border: none;
  border-radius: 10px;
  background: #C8A67E;
  color: #fff;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-confirm:hover {
  background: #b8966e;
}

.toast {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: #5D4E42;
  color: #fff;
  padding: 14px 24px;
  border-radius: 8px;
  font-weight: 500;
  z-index: 200;
}
</style>
