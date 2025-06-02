<template>
  <div class="order-form">
    <h2>☕ 커피 주문하기</h2>

    <!-- 이름 입력 -->
    <div class="form-section">
      <label class="form-label">이름 *</label>
      <input
        v-model="order.name"
        type="text"
        placeholder="이름을 입력하세요"
        class="form-input"
        required
      />
    </div>

    <!-- 음료 선택 -->
    <div class="form-section">
      <label class="form-label">음료 선택 *</label>
      <div v-if="menu" class="menu-categories">
        <div
          v-for="category in menu.categories"
          :key="category.name"
          class="category"
        >
          <h4 class="category-title">{{ category.name }}</h4>
          <div class="menu-grid">
            <div
              v-for="item in category.items"
              :key="item.name"
              :class="['menu-card', { selected: order.drink === item.name }]"
              @click="selectDrink(item)"
            >
              <h5 class="menu-name">{{ item.name }}</h5>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 옵션 선택 (음료가 선택된 경우에만) -->
    <div v-if="selectedDrinkItem && hasOptions" class="options-section">
      <h3 class="options-title">옵션 선택</h3>

      <!-- 온도 선택 -->
      <div v-if="selectedDrinkItem.options.temperature" class="form-section">
        <label class="form-label">{{ getOptionLabel('temperature') }} *</label>
        <div class="option-grid">
          <div
            v-for="temp in selectedDrinkItem.options.temperature"
            :key="temp"
            :class="['option-card', { selected: order.temperature === temp }]"
            @click="order.temperature = temp"
          >
            <span class="option-name">{{ temp }}</span>
          </div>
        </div>
      </div>

      <!-- 원두 선택 (커피인 경우) -->
      <div v-if="selectedDrinkItem.options.beans" class="form-section">
        <label class="form-label">{{ getOptionLabel('beans') }} *</label>
        <div class="option-grid">
          <div
            v-for="bean in selectedDrinkItem.options.beans"
            :key="bean"
            :class="['option-card', { selected: order.beans === bean }]"
            @click="order.beans = bean"
          >
            <span class="option-name">{{ bean }}</span>
          </div>
        </div>
      </div>

      <!-- 우유 종류 선택 (우유 음료인 경우) -->
      <div v-if="selectedDrinkItem.options.milk" class="form-section">
        <label class="form-label">{{ getOptionLabel('milk') }} *</label>
        <div class="option-grid">
          <div
            v-for="milk in selectedDrinkItem.options.milk"
            :key="milk"
            :class="['option-card', { selected: order.milk === milk }]"
            @click="order.milk = milk"
          >
            <span class="option-name">{{ milk }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 옵션이 없는 음료 안내 -->
    <div v-if="selectedDrinkItem && !hasOptions" class="no-options-info">
      <div class="info-card">
        <span class="info-icon">✅</span>
        <span class="info-text">{{ order.drink }}은(는) 추가 옵션이 없습니다.</span>
      </div>
    </div>

    <!-- 주문 요약 -->
    <div v-if="order.drink" class="order-summary">
      <h3 class="summary-title">주문 내용</h3>
      <div class="summary-content">
        <div class="summary-item">
          <span class="summary-label">음료:</span>
          <span class="summary-value">{{ order.drink }}</span>
        </div>
        <div v-if="order.temperature" class="summary-item">
          <span class="summary-label">온도:</span>
          <span class="summary-value">{{ order.temperature }}</span>
        </div>
        <div v-if="order.beans" class="summary-item">
          <span class="summary-label">원두:</span>
          <span class="summary-value">{{ order.beans }}</span>
        </div>
        <div v-if="order.milk" class="summary-item">
          <span class="summary-label">우유:</span>
          <span class="summary-value">{{ order.milk }}</span>
        </div>
      </div>
    </div>

    <!-- 주문 버튼 -->
    <div class="form-actions">
      <button
        @click="submitOrder"
        :disabled="!canSubmit"
        class="submit-btn"
      >
        {{ editMode ? '주문 수정' : '주문하기' }}
      </button>

      <button
        v-if="editMode"
        @click="cancelEdit"
        class="cancel-btn"
      >
        취소
      </button>

      <button
        v-if="order.name || order.drink"
        @click="resetForm"
        class="reset-btn"
      >
        초기화
      </button>
    </div>

    <!-- 성공 메시지 -->
    <div v-if="showSuccess" class="success-message">
      {{ editMode ? '주문이 수정되었습니다!' : '주문이 완료되었습니다!' }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'OrderForm',
  props: {
    menu: Object
  },
  emits: ['order-submitted', 'order-updated'],
  data() {
    return {
      order: {
        name: '',
        drink: '',
        temperature: '',
        beans: '',
        milk: ''
      },
      editMode: false,
      editOrderId: null,
      showSuccess: false
    }
  },
  computed: {
    selectedDrinkItem() {
      if (!this.menu || !this.order.drink) return null

      for (const category of this.menu.categories) {
        const item = category.items.find(item => item.name === this.order.drink)
        if (item) return item
      }
      return null
    },

    hasOptions() {
      if (!this.selectedDrinkItem || !this.selectedDrinkItem.options) return false
      return Object.keys(this.selectedDrinkItem.options).length > 0
    },

    canSubmit() {
      if (!this.order.name.trim() || !this.order.drink) return false

      // 옵션이 없는 음료는 바로 주문 가능
      if (!this.hasOptions) return true

      // 옵션이 있는 음료는 필수 옵션 확인
      const options = this.selectedDrinkItem.options

      // 온도 옵션이 있으면 반드시 선택해야 함
      if (options.temperature && !this.order.temperature) return false

      // 원두 옵션이 있으면 반드시 선택해야 함
      if (options.beans && !this.order.beans) return false

      // 우유 옵션이 있으면 반드시 선택해야 함
      if (options.milk && !this.order.milk) return false

      return true
    }
  },
  methods: {
    selectDrink(drink) {
      this.order.drink = drink.name
      // 음료 변경시 모든 옵션 리셋
      this.order.temperature = ''
      this.order.beans = ''
      this.order.milk = ''

      // 온도 옵션이 하나뿐이면 자동 선택
      if (drink.options.temperature && drink.options.temperature.length === 1) {
        this.order.temperature = drink.options.temperature[0]
      }

      // 원두 옵션이 하나뿐이면 자동 선택
      if (drink.options.beans && drink.options.beans.length === 1) {
        this.order.beans = drink.options.beans[0]
      }

      // 우유 옵션이 하나뿐이면 자동 선택
      if (drink.options.milk && drink.options.milk.length === 1) {
        this.order.milk = drink.options.milk[0]
      }
    },

    getOptionLabel(optionType) {
      const labels = {
        temperature: '온도',
        beans: '원두',
        milk: '우유 종류'
      }
      return labels[optionType] || optionType
    },

    async submitOrder() {
      if (!this.canSubmit) return

      try {
        // 주문 데이터 구성 (빈 값 제거)
        const orderData = {
          name: this.order.name,
          drink: this.order.drink,
          ...(this.order.temperature && { temperature: this.order.temperature }),
          ...(this.order.beans && { beans: this.order.beans }),
          ...(this.order.milk && { milk: this.order.milk })
        }

        const url = this.editMode
          ? `http://localhost:5000/api/orders/${this.editOrderId}`
          : 'http://localhost:5000/api/orders'

        const method = this.editMode ? 'PUT' : 'POST'

        const response = await fetch(url, {
          method,
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(orderData)
        })

        if (response.ok) {
          this.showSuccessMessage()
          this.resetForm()
          this.$emit(this.editMode ? 'order-updated' : 'order-submitted')
        } else {
          throw new Error('서버 오류가 발생했습니다.')
        }
      } catch (error) {
        console.error('주문 실패:', error)
        alert('주문에 실패했습니다. 다시 시도해주세요.')
      }
    },

    showSuccessMessage() {
      this.showSuccess = true
      setTimeout(() => {
        this.showSuccess = false
      }, 3000)
    },

    resetForm() {
      this.order = {
        name: '',
        drink: '',
        temperature: '',
        beans: '',
        milk: ''
      }
      this.editMode = false
      this.editOrderId = null
    },

    cancelEdit() {
      this.resetForm()
    },

    editOrder(orderData) {
      this.order = { ...orderData }
      this.editMode = true
      this.editOrderId = orderData.id
    }
  }
}
</script>

<style scoped>
.order-form {
  max-width: 800px;
  margin: 0 auto;
}

.order-form h2 {
  color: #8B4513;
  margin-bottom: 2rem;
  text-align: center;
  font-size: 1.8rem;
}

.form-section {
  margin-bottom: 2rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #333;
  font-size: 1.1rem;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #8B4513;
}

.category {
  margin-bottom: 1.5rem;
}

.category-title {
  color: #8B4513;
  margin-bottom: 0.75rem;
  font-size: 1.2rem;
  border-bottom: 2px solid #8B4513;
  padding-bottom: 0.25rem;
}

.menu-grid, .option-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.menu-card, .option-card {
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  background: #fafafa;
}

.menu-card:hover, .option-card:hover {
  border-color: #8B4513;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 69, 19, 0.2);
}

.menu-card.selected, .option-card.selected {
  border-color: #8B4513;
  background: linear-gradient(135deg, #8B4513, #D2691E);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 69, 19, 0.3);
}

.menu-name {
  font-size: 1.1rem;
  font-weight: bold;
  margin: 0;
}

.option-name {
  font-weight: bold;
  font-size: 1rem;
}

.options-section {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 10px;
  margin-bottom: 2rem;
  border: 1px solid #e9ecef;
}

.options-title {
  color: #8B4513;
  margin-bottom: 1.5rem;
  font-size: 1.3rem;
  text-align: center;
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 0.5rem;
}

.no-options-info {
  margin-bottom: 2rem;
}

.info-card {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #d1edff;
  border: 1px solid #b6d7ff;
  border-radius: 8px;
  padding: 1rem;
  color: #0c5aa6;
}

.info-icon {
  font-size: 1.2rem;
}

.info-text {
  font-weight: 500;
}

.order-summary {
  background: #f9f9f9;
  padding: 1.5rem;
  border-radius: 10px;
  margin-bottom: 2rem;
  border: 1px solid #e0e0e0;
}

.summary-title {
  color: #8B4513;
  margin-bottom: 1rem;
  font-size: 1.2rem;
  text-align: center;
}

.summary-content {
  max-width: 400px;
  margin: 0 auto;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e0e0e0;
}

.summary-item:last-child {
  border-bottom: none;
}

.summary-label {
  font-weight: bold;
  color: #666;
}

.summary-value {
  font-weight: bold;
  color: #8B4513;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.submit-btn, .cancel-btn, .reset-btn {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.submit-btn {
  background: linear-gradient(135deg, #8B4513, #D2691E);
  color: white;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 69, 19, 0.3);
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.cancel-btn {
  background: #6c757d;
  color: white;
}

.cancel-btn:hover {
  background: #5a6268;
  transform: translateY(-2px);
}

.reset-btn {
  background: #dc3545;
  color: white;
}

.reset-btn:hover {
  background: #c82333;
  transform: translateY(-2px);
}

.success-message {
  background: #d4edda;
  color: #155724;
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  margin-top: 1rem;
  border: 1px solid #c3e6cb;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .menu-grid, .option-grid {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  }

  .form-actions {
    flex-direction: column;
    align-items: center;
  }

  .submit-btn, .cancel-btn, .reset-btn {
    width: 100%;
    max-width: 300px;
  }

  .summary-content {
    max-width: none;
  }
}
</style>