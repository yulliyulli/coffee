<!-- AdminPanel.vue -->
<template>
  <div class="admin-container">
    <header class="admin-header">
      <h1>📊 주문 관리자 화면</h1>
      <div class="header-actions">
        <div v-if="activeCart" class="active-cart-badge">
          🛒 {{ activeCart.name }} ({{ activeCart.cafe }})
          <span v-if="activeCart.single_order" class="single-order-tag">1인1메뉴</span>
        </div>
        <button @click="goToKiosk" class="kiosk-btn">키오스크로 이동</button>
      </div>
    </header>

    <!-- 주문함 관리 섹션 -->
    <div class="cart-section">
      <div class="cart-header">
        <h2>🛒 주문함 관리</h2>
        <button @click="showCartModal = true" class="new-cart-btn">
          ➕ 새 주문함
        </button>
      </div>

      <div class="cart-list">
        <div
          v-for="cart in carts"
          :key="cart.id"
          :class="['cart-item', { active: cart.is_active }]"
        >
          <div class="cart-info">
            <span class="cart-name">{{ cart.name }}</span>
            <span class="cart-cafe">{{ cart.cafe }}</span>
            <span class="cart-count">{{ cart.order_count }}명 주문</span>
          </div>
          <div class="cart-actions">
            <button
              v-if="!cart.is_active"
              @click="activateCart(cart.id)"
              class="activate-btn"
            >
              선택
            </button>
            <span v-else class="active-label">활성</span>
            <button @click="deleteCart(cart.id)" class="delete-btn">삭제</button>
          </div>
        </div>
        <div v-if="carts.length === 0" class="empty-cart-message">
          주문함가 없습니다. 새 주문함를 생성해주세요.
        </div>
      </div>
    </div>

    <!-- 통계 요약 -->
    <div class="stats-summary">
      <div class="stat-card">
        <h3>총 주문 수</h3>
        <div class="stat-value">{{ orderData.total_orders }}</div>
      </div>
      <div class="stat-card">
        <h3>총 고객 수</h3>
        <div class="stat-value">{{ orderData.total_customers }}</div>
      </div>
      <div class="stat-card">
        <h3>총 음료 수</h3>
        <div class="stat-value">{{ orderData.total_items }}</div>
      </div>
    </div>

    <!-- 액션 버튼 -->
    <div class="action-buttons">
      <button @click="showNewOrderModal = true" class="new-order-btn">
        ➕ 주문 수동 추가
      </button>
      <button @click="refreshData" class="refresh-btn" :disabled="loading">
        {{ loading ? '새로고침 중...' : '🔄 새로고침' }}
      </button>
      <button @click="downloadText" class="text-btn">
        📄 텍스트 다운로드
      </button>
    </div>

    <!-- 뷰 전환 탭 -->
    <div class="view-tabs">
      <button
        @click="currentView = 'summary'"
        :class="{ active: currentView === 'summary' }"
        class="view-tab"
      >
        📦 메뉴별 수량
      </button>
      <button
        @click="currentView = 'customers'"
        :class="{ active: currentView === 'customers' }"
        class="view-tab"
      >
        👥 고객별 주문
      </button>
      <button
        @click="currentView = 'orders'"
        :class="{ active: currentView === 'orders' }"
        class="view-tab"
      >
        📋 전체 주문
      </button>
    </div>

    <!-- 메뉴별 수량 화면 -->
    <div v-if="currentView === 'summary'" class="summary-section">
      <h2>📦 메뉴별 주문 수량</h2>

      <div v-if="loading" class="loading-message">
        데이터를 불러오는 중...
      </div>

      <div v-else-if="groupedItems.length === 0" class="empty-message">
        주문 내역이 없습니다.
      </div>

      <div v-else class="summary-table-container">
        <table class="summary-table">
          <thead>
            <tr>
              <th>메뉴</th>
              <th>옵션</th>
              <th>수량</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in groupedItems" :key="index">
              <td class="menu-name">{{ item.name }}</td>
              <td class="menu-options">{{ item.options || '-' }}</td>
              <td class="menu-qty">{{ item.qty }}개</td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <td colspan="2"><strong>총계</strong></td>
              <td class="menu-qty"><strong>{{ totalQty }}개</strong></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>

    <!-- 고객별 주문 내역 화면 -->
    <div v-if="currentView === 'customers'" class="customers-section">
      <h2>👥 고객별 주문 요약 (총 {{ orderData.total_customers }}명)</h2>

      <div v-if="loading" class="loading-message">
        데이터를 불러오는 중...
      </div>

      <div v-else-if="orderData.customers_summary.length === 0" class="empty-message">
        주문 내역이 없습니다.
      </div>

      <div v-else class="customers-grid">
        <div
          v-for="customer in orderData.customers_summary"
          :key="customer.customer_name"
          class="customer-card"
        >
          <div class="customer-header">
            <h3 class="customer-name">{{ customer.customer_name }}</h3>
            <div class="customer-stats">
              <span class="stat-badge orders">{{ customer.order_count }}회 주문</span>
              <span class="stat-badge items">{{ customer.total_items }}개 음료</span>
            </div>
          </div>

          <div class="customer-info">
            <div class="last-order">
              <strong>최근 주문:</strong> {{ customer.last_order_date }}
            </div>
          </div>

          <div class="customer-orders">
            <h4>주문 내역</h4>
            <div class="orders-summary">
              {{ customer.all_items_summary }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 전체 주문 내역 화면 -->
    <div v-if="currentView === 'orders'" class="orders-section">
      <h2>📋 전체 주문 내역</h2>

      <div v-if="loading" class="loading-message">
        데이터를 불러오는 중...
      </div>

      <div v-else-if="orderData.orders.length === 0" class="empty-message">
        주문 내역이 없습니다.
      </div>

      <div v-else class="orders-table-container">
        <table class="orders-table">
          <thead>
            <tr>
              <th>번호</th>
              <th>고객명</th>
              <th>주문내용</th>
              <th>음료수</th>
              <th>주문일시</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(order, index) in orderData.orders" :key="order.id">
              <td class="text-center">{{ index + 1 }}</td>
              <td class="customer-name-cell">{{ order.customer_name }}</td>
              <td class="order-content">{{ order.items_text }}</td>
              <td class="text-center">{{ order.items_count }}개</td>
              <td class="text-center">
                <div class="datetime">
                  <div class="date">{{ order.order_date }}</div>
                  <div class="time">{{ order.order_time }}</div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 새 주문함 생성 모달 -->
    <div v-if="showCartModal" class="modal-overlay" @click.self="showCartModal = false">
      <div class="modal">
        <h2>🛒 새 주문함 생성</h2>

        <div class="form-group">
          <label>주문함 이름</label>
          <input v-model="newCart.name" type="text" placeholder="예: 3월 5일 오후 주문" />
        </div>

        <div class="form-group">
          <label>카페 선택</label>
          <div class="cafe-buttons">
            <button
              v-for="cafe in cafeOptions"
              :key="cafe"
              :class="['cafe-btn', { active: newCart.cafe === cafe }]"
              @click="newCart.cafe = cafe"
            >
              {{ cafe }}
            </button>
          </div>
        </div>

        <div class="form-group checkbox-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="newCart.singleOrder" />
            <span>1인 1메뉴 제한</span>
          </label>
          <small class="input-hint">체크하면 한 사람당 하나의 메뉴만 주문할 수 있습니다</small>
        </div>

        <div class="modal-actions">
          <button @click="showCartModal = false" class="cancel-btn">취소</button>
          <button @click="createCart" class="submit-btn" :disabled="!canCreateCart">생성</button>
        </div>
      </div>
    </div>

    <!-- 새 주문 수동 추가 모달 -->
    <div v-if="showNewOrderModal" class="modal-overlay" @click.self="showNewOrderModal = false">
      <div class="modal">
        <h2>➕ 주문 수동 추가</h2>

        <div class="form-group">
          <label>고객 이름</label>
          <input v-model="newOrder.customerName" type="text" placeholder="이름 입력" />
        </div>

        <div class="form-group">
          <label>메뉴명</label>
          <input v-model="newOrder.menuName" type="text" placeholder="예: 아메리카노 (ICE)" />
          <small class="input-hint">옵션이 있다면 괄호 안에 입력하세요</small>
        </div>

        <div class="modal-actions">
          <button @click="showNewOrderModal = false" class="cancel-btn">취소</button>
          <button @click="createOrder" class="submit-btn" :disabled="!canCreateOrder">주문 추가</button>
        </div>
      </div>
    </div>

    <!-- 에러/성공 토스트 -->
    <div v-if="toast.show" :class="['toast', toast.type]">
      {{ toast.message }}
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'AdminPanel',
  data() {
    return {
      // 주문함 관련
      carts: [],
      activeCart: null,
      showCartModal: false,
      newCart: {
        name: '',
        cafe: '',
        singleOrder: false
      },
      cafeOptions: ['파란만잔', '텐퍼센트'],

      // 뷰 관련
      currentView: 'summary',
      orderData: {
        orders: [],
        customers_summary: [],
        total_orders: 0,
        total_customers: 0,
        total_items: 0
      },
      menu: { categories: [] },
      loading: false,

      // 주문 생성 관련
      showNewOrderModal: false,
      newOrder: {
        customerName: '',
        menuName: ''
      },

      // 토스트
      toast: {
        show: false,
        message: '',
        type: 'success'
      }
    }
  },
  computed: {
    canCreateCart() {
      return this.newCart.name.trim() && this.newCart.cafe
    },
    groupedItems() {
      const groups = {}

      for (const order of this.orderData.orders || []) {
        const items = order.items_text?.split(' | ') || []
        for (const item of items) {
          const key = item.trim()
          if (key) {
            groups[key] = (groups[key] || 0) + 1
          }
        }
      }

      // Parse into name and options
      return Object.entries(groups)
        .map(([key, qty]) => {
          const match = key.match(/^(.+?)\s*\((.+)\)$/)
          if (match) {
            return { name: match[1], options: match[2], qty }
          }
          return { name: key, options: '', qty }
        })
        .sort((a, b) => b.qty - a.qty)
    },
    totalQty() {
      return this.groupedItems.reduce((sum, item) => sum + item.qty, 0)
    },
    canCreateOrder() {
      return this.newOrder.customerName.trim() && this.newOrder.menuName.trim()
    }
  },
  async mounted() {
    await Promise.all([
      this.loadCarts(),
      this.loadMenu()
    ])

    // 주문함 로드 후 주문 데이터 로드
    await this.loadOrderData()

    this.autoRefreshInterval = setInterval(() => {
      this.loadOrderData()
    }, 30000)
  },
  beforeUnmount() {
    if (this.autoRefreshInterval) {
      clearInterval(this.autoRefreshInterval)
    }
  },
  methods: {
    // 주문함 관련 메서드
    async loadCarts() {
      try {
        const [cartsRes, activeRes] = await Promise.all([
          axios.get('/api/carts'),
          axios.get('/api/carts/active')
        ])
        this.carts = cartsRes.data.carts || []
        this.activeCart = activeRes.data.cart
      } catch (e) {
        console.error('주문함 로드 실패:', e)
      }
    },
    async createCart() {
      if (!this.canCreateCart) return

      try {
        await axios.post('/api/carts', {
          name: this.newCart.name,
          cafe: this.newCart.cafe,
          single_order: this.newCart.singleOrder
        })

        this.showToast(`'${this.newCart.name}' 주문함이 생성되었습니다!`, 'success')
        this.showCartModal = false
        this.newCart = { name: '', cafe: '', singleOrder: false }

        await this.loadCarts()
        await this.loadOrderData()
      } catch (e) {
        console.error('주문함 생성 실패:', e)
        this.showToast('주문함 생성에 실패했습니다.', 'error')
      }
    },
    async activateCart(cartId) {
      try {
        await axios.put(`/api/carts/${cartId}/activate`)
        await this.loadCarts()
        await this.loadOrderData()
        this.showToast('주문함가 변경되었습니다.', 'success')
      } catch (e) {
        console.error('주문함 활성화 실패:', e)
        this.showToast('주문함 활성화에 실패했습니다.', 'error')
      }
    },
    async deleteCart(cartId) {
      if (!confirm('정말 이 주문함를 삭제하시겠습니까?\n주문함에 담긴 모든 주문도 함께 삭제됩니다.')) {
        return
      }

      try {
        await axios.delete(`/api/carts/${cartId}`)
        await this.loadCarts()
        await this.loadOrderData()
        this.showToast('주문함가 삭제되었습니다.', 'success')
      } catch (e) {
        console.error('주문함 삭제 실패:', e)
        this.showToast('주문함 삭제에 실패했습니다.', 'error')
      }
    },

    // 메뉴 및 주문 관련 메서드
    async loadMenu() {
      try {
        const { data } = await axios.get('/api/menu')
        this.menu = data
      } catch (e) {
        console.error('메뉴 로드 실패:', e)
      }
    },
    async loadOrderData() {
      this.loading = true
      try {
        const response = await axios.get('/api/admin/orders')
        this.orderData = response.data
      } catch (error) {
        console.error('주문 데이터 로드 실패:', error)
        this.showToast('주문 데이터를 불러오는데 실패했습니다.', 'error')
      } finally {
        this.loading = false
      }
    },
    async refreshData() {
      await Promise.all([this.loadCarts(), this.loadOrderData()])
      this.showToast('새로고침 완료!', 'success')
    },
    async createOrder() {
      if (!this.canCreateOrder) return

      try {
        const orderItem = {
          name: this.newOrder.menuName.trim(),
          options: {}
        }

        await axios.post(`/api/orders/${this.newOrder.customerName}/items`, orderItem)

        this.showToast(`${this.newOrder.customerName}님의 주문이 추가되었습니다!`, 'success')
        this.showNewOrderModal = false
        this.newOrder = { customerName: '', menuName: '' }
        await this.loadOrderData()
      } catch (e) {
        console.error('주문 생성 실패:', e)
        this.showToast('주문 생성에 실패했습니다.', 'error')
      }
    },

    // 다운로드 관련 메서드
    downloadText() {
      if (this.groupedItems.length === 0) {
        this.showToast('다운로드할 주문이 없습니다.', 'error')
        return
      }

      const cafeName = this.activeCart?.cafe || '카페'
      const cartName = this.activeCart?.name || '주문함'

      let text = `[${cafeName}] ${cartName} 주문 요약\n`
      text += `생성일시: ${new Date().toLocaleString('ko-KR')}\n`
      text += `총 ${this.totalQty}잔\n`
      text += '─'.repeat(40) + '\n\n'

      for (const item of this.groupedItems) {
        const options = item.options ? ` (${item.options})` : ''
        text += `${item.name}${options} - ${item.qty}개\n`
      }

      text += '\n' + '─'.repeat(40) + '\n'
      text += `합계: ${this.totalQty}개\n`

      const blob = new Blob([text], { type: 'text/plain;charset=utf-8' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      const now = new Date()
      link.download = `주문요약_${cafeName}_${now.getFullYear()}${String(now.getMonth()+1).padStart(2,'0')}${String(now.getDate()).padStart(2,'0')}.txt`
      link.click()
      window.URL.revokeObjectURL(url)

      this.showToast('텍스트 파일 다운로드 완료!', 'success')
    },

    // 유틸리티 메서드
    goToKiosk() {
      this.$router.push('/')
    },
    showToast(message, type = 'success') {
      this.toast = { show: true, message, type }
      setTimeout(() => {
        this.toast.show = false
      }, 3000)
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

.admin-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  min-height: 100vh;
  background: #F5F0EA;
}

.admin-header {
  background: #C8A67E;
  color: #3A3330;
  padding: 20px 24px;
  border-radius: 12px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.admin-header h1 {
  margin: 0;
  font-size: 1.5rem;
  color: #3A3330;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.active-cart-badge {
  background: #C8A67E;
  color: #3A3330;
  padding: 10px 16px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.single-order-tag {
  background: #3A3330;
  color: #FFFBF5;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.kiosk-btn {
  padding: 10px 20px;
  border: 2px solid #3A3330;
  border-radius: 8px;
  background: rgba(255, 251, 245, 0.85);
  color: #3A3330;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.kiosk-btn:hover {
  background: #3A3330;
  color: #FFFBF5;
}

/* 주문함 섹션 */
.cart-section {
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(58,51,48,0.06);
}

.cart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.cart-header h2 {
  margin: 0;
  font-size: 1.2rem;
  color: #3A3330;
}

.new-cart-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  background: #C8A67E;
  color: #fff;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.new-cart-btn:hover {
  background: #b8966e;
}

.cart-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cart-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border: 1px solid #E8E0D8;
  border-radius: 8px;
  background: #FFFBF5;
  transition: all 0.2s;
}

.cart-item.active {
  border-color: #C8A67E;
  background: #fff;
  box-shadow: 0 2px 8px rgba(200,166,126,0.2);
}

.cart-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.cart-name {
  font-weight: 600;
  font-size: 1rem;
  color: #3A3330;
}

.cart-cafe {
  color: #5D4E42;
  font-size: 0.9rem;
  padding: 4px 10px;
  background: #F5F0EA;
  border-radius: 12px;
}

.cart-count {
  color: #8B7355;
  font-size: 0.85rem;
}

.cart-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.activate-btn {
  padding: 6px 14px;
  border: 1px solid #3A3330;
  border-radius: 6px;
  background: #fff;
  color: #3A3330;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.activate-btn:hover {
  background: #3A3330;
  color: #FFFBF5;
}

.active-label {
  padding: 6px 14px;
  background: #7a9a7a;
  color: white;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
}

.delete-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  background: #b87070;
  color: white;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.delete-btn:hover {
  background: #a86060;
}

.empty-cart-message {
  text-align: center;
  padding: 20px;
  color: #8B7355;
}

.stats-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(58,51,48,0.06);
}

.stat-card h3 {
  color: #8B7355;
  font-size: 0.9rem;
  margin: 0 0 8px 0;
  font-weight: 500;
}

.stat-value {
  color: #3A3330;
  font-size: 2rem;
  font-weight: 700;
}

.action-buttons {
  background: #fff;
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 20px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(58,51,48,0.06);
}

.action-buttons button {
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.new-order-btn {
  background: #C8A67E;
  color: #fff;
}

.new-order-btn:hover {
  background: #b8966e;
}

.refresh-btn {
  background: #7a9aaa;
  color: white;
}

.refresh-btn:hover {
  background: #6a8a9a;
}

.text-btn {
  background: #8B7355;
  color: white;
}

.text-btn:hover {
  background: #7a6345;
}

.action-buttons button:disabled {
  background: #E8E0D8;
  color: #8B7355;
  cursor: not-allowed;
}

.view-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.view-tab {
  flex: 1;
  padding: 14px;
  border: 1px solid #E8E0D8;
  background: #fff;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  color: #5D4E42;
}

.view-tab:hover {
  border-color: #C8A67E;
  background: #FFFBF5;
}

.view-tab.active {
  background: #3A3330;
  color: #FFFBF5;
  border-color: #3A3330;
}

/* Summary Section */
.summary-section, .customers-section, .orders-section {
  background: #fff;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(58,51,48,0.06);
}

.summary-section h2, .customers-section h2, .orders-section h2 {
  margin: 0 0 20px 0;
  font-size: 1.2rem;
  color: #3A3330;
}

.summary-table-container, .orders-table-container {
  overflow-x: auto;
}

.summary-table, .orders-table {
  width: 100%;
  border-collapse: collapse;
}

.summary-table th, .summary-table td,
.orders-table th, .orders-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #E8E0D8;
}

.summary-table th, .orders-table th {
  background: #F5F0EA;
  font-weight: 600;
  color: #3A3330;
}

.summary-table tfoot td {
  background: #F5F0EA;
  font-weight: 600;
}

.menu-name {
  font-weight: 500;
  color: #3A3330;
}

.menu-options {
  color: #8B7355;
  font-size: 0.9rem;
}

.menu-qty {
  text-align: center;
  font-weight: 600;
  color: #3A3330;
}

.loading-message, .empty-message {
  text-align: center;
  padding: 40px;
  color: #8B7355;
}

/* Customers Grid */
.customers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.customer-card {
  background: #FFFBF5;
  border: 1px solid #E8E0D8;
  border-radius: 12px;
  padding: 16px;
}

.customer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.customer-name {
  margin: 0;
  font-size: 1.1rem;
  color: #3A3330;
}

.customer-stats {
  display: flex;
  gap: 6px;
}

.stat-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.stat-badge.orders {
  background: #F5F0EA;
  color: #5D4E42;
}

.stat-badge.items {
  background: #e8f0e8;
  color: #4a6a4a;
}

.customer-info {
  margin-bottom: 12px;
}

.last-order {
  color: #8B7355;
  font-size: 0.85rem;
}

.customer-orders h4 {
  margin: 0 0 8px 0;
  font-size: 0.9rem;
  color: #3A3330;
}

.orders-summary {
  background: #fff;
  padding: 12px;
  border-radius: 8px;
  font-size: 0.85rem;
  line-height: 1.4;
  color: #5D4E42;
  border-left: 3px solid #C8A67E;
  max-height: 100px;
  overflow-y: auto;
}

/* Orders Table */
.text-center {
  text-align: center;
}

.customer-name-cell {
  font-weight: 600;
  color: #3A3330;
}

.order-content {
  max-width: 300px;
  word-wrap: break-word;
  color: #3A3330;
}

.datetime .date {
  font-weight: 500;
  color: #3A3330;
}

.datetime .time {
  font-size: 0.85rem;
  color: #8B7355;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(58,51,48,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: #fff;
  padding: 24px;
  border-radius: 16px;
  width: 90%;
  max-width: 400px;
}

.modal h2 {
  margin: 0 0 20px 0;
  font-size: 1.3rem;
  color: #3A3330;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #3A3330;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 12px;
  border: 1px solid #E8E0D8;
  border-radius: 8px;
  font-size: 1rem;
  box-sizing: border-box;
  background: #FFFBF5;
  color: #3A3330;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #C8A67E;
  background: #fff;
}

.input-hint {
  display: block;
  margin-top: 6px;
  font-size: 0.8rem;
  color: #8B7355;
}

.checkbox-group {
  margin-top: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-weight: 500;
  color: #3A3330;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: #C8A67E;
  cursor: pointer;
}

.cafe-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.cafe-btn {
  padding: 12px;
  border: 1px solid #E8E0D8;
  border-radius: 8px;
  background: #FFFBF5;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
  color: #5D4E42;
}

.cafe-btn:hover {
  border-color: #C8A67E;
  background: #fff;
}

.cafe-btn.active {
  background: #3A3330;
  color: #FFFBF5;
  border-color: #3A3330;
}

.option-buttons {
  display: flex;
  gap: 8px;
}

.option-btn {
  flex: 1;
  padding: 12px;
  border: 1px solid #E8E0D8;
  border-radius: 8px;
  background: #FFFBF5;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  color: #5D4E42;
}

.option-btn:hover {
  border-color: #C8A67E;
  background: #fff;
}

.option-btn.active {
  background: #3A3330;
  color: #FFFBF5;
  border-color: #3A3330;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.cancel-btn, .submit-btn {
  flex: 1;
  padding: 14px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
}

.cancel-btn {
  background: #F5F0EA;
  color: #5D4E42;
}

.cancel-btn:hover {
  background: #E8E0D8;
}

.submit-btn {
  background: #C8A67E;
  color: #fff;
}

.submit-btn:hover {
  background: #b8966e;
}

.submit-btn:disabled {
  background: #E8E0D8;
  color: #8B7355;
  cursor: not-allowed;
}

/* Toast */
.toast {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 14px 24px;
  border-radius: 8px;
  font-weight: 500;
  z-index: 2000;
}

.toast.success {
  background: #7a9a7a;
  color: white;
}

.toast.error {
  background: #b87070;
  color: white;
}

/* Responsive */
@media (max-width: 768px) {
  .admin-header {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }

  .header-actions {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }

  .stats-summary {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-buttons button {
    width: 100%;
  }

  .view-tabs {
    flex-direction: column;
  }

  .customers-grid {
    grid-template-columns: 1fr;
  }

  .cart-item {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .cart-info {
    flex-wrap: wrap;
  }

  .cart-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
