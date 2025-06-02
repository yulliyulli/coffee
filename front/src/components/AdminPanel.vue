<!-- AdminPanel.vue -->
<template>
  <div class="admin-container">
    <header class="admin-header">
      <h1>📊 주문 관리자 화면</h1>
      <button @click="goToKiosk" class="kiosk-btn">키오스크로 이동</button>
    </header>

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
      <button @click="refreshData" class="refresh-btn" :disabled="loading">
        {{ loading ? '새로고침 중...' : '🔄 새로고침' }}
      </button>
      <button @click="downloadExcel" class="excel-btn" :disabled="downloading">
        {{ downloading ? '다운로드 중...' : '📊 엑셀 다운로드' }}
      </button>
    </div>

    <!-- 뷰 전환 탭 -->
    <div class="view-tabs">
      <button 
        @click="currentView = 'customers'" 
        :class="{ active: currentView === 'customers' }" 
        class="view-tab"
      >
        👥 고객별 주문 내역
      </button>
      <button 
        @click="currentView = 'orders'" 
        :class="{ active: currentView === 'orders' }" 
        class="view-tab"
      >
        📋 전체 주문 내역
      </button>
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
          
          <!-- 상세 주문 목록 (접기/펼치기) -->
          <div class="order-details">
            <button 
              @click="toggleCustomerDetails(customer.customer_name)"
              class="toggle-details-btn"
            >
              {{ expandedCustomers.has(customer.customer_name) ? '접기' : '상세보기' }}
            </button>
            
            <div v-if="expandedCustomers.has(customer.customer_name)" class="detailed-orders">
              <div 
                v-for="(order, index) in customer.orders_detail" 
                :key="index" 
                class="order-detail-item"
              >
                <div class="order-id">주문번호: {{ order.order_id }}</div>
                <div class="order-date">{{ order.date }}</div>
                <div class="order-items">
                  <div v-for="(item, itemIndex) in order.items" :key="itemIndex" class="order-item">
                    • {{ item }}
                  </div>
                </div>
              </div>
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
              <th>주문번호</th>
              <th>고객명</th>
              <th>주문내용</th>
              <th>음료수</th>
              <th>주문일시</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(order, index) in orderData.orders" :key="order.id" :class="{ 'even-row': index % 2 === 0 }">
              <td class="text-center">{{ index + 1 }}</td>
              <td class="text-center">{{ order.order_id }}</td>
              <td class="customer-name">{{ order.customer_name }}</td>
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
  name: 'AdminPanel',
  data() {
    return {
      currentView: 'customers', // 'customers' or 'orders'
      orderData: {
        orders: [],
        customers_summary: [],
        total_orders: 0,
        total_customers: 0,
        total_items: 0
      },
      loading: false,
      downloading: false,
      errorMessage: '',
      expandedCustomers: new Set() // 상세 정보가 펼쳐진 고객들
    }
  },
  async mounted() {
    await this.loadOrderData()
    
    // 30초마다 자동 새로고침
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
    async loadOrderData() {
      this.loading = true
      try {
        const response = await axios.get('/api/admin/orders')
        this.orderData = response.data
        console.log('주문 데이터 로드 완료:', this.orderData.total_orders, '개 주문')
        console.log('고객별 요약:', this.orderData.customers_summary?.length || 0, '명')
      } catch (error) {
        console.error('주문 데이터 로드 실패:', error)
        this.showError('주문 데이터를 불러오는데 실패했습니다.')
      } finally {
        this.loading = false
      }
    },

    async refreshData() {
      await this.loadOrderData()
    },

    async downloadExcel() {
      this.downloading = true
      try {
        const response = await axios.get('/api/admin/orders/excel', {
          responseType: 'blob'
        })
        
        // 파일 다운로드
        const blob = new Blob([response.data], {
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        
        // 파일명 생성
        const now = new Date()
        const filename = `주문내역_${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}.xlsx`
        link.download = filename
        
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        console.log('엑셀 파일 다운로드 완료:', filename)
        
      } catch (error) {
        console.error('엑셀 다운로드 실패:', error)
        this.showError('엑셀 파일 다운로드에 실패했습니다.')
      } finally {
        this.downloading = false
      }
    },

    toggleCustomerDetails(customerName) {
      if (this.expandedCustomers.has(customerName)) {
        this.expandedCustomers.delete(customerName)
      } else {
        this.expandedCustomers.add(customerName)
      }
    },

    goToKiosk() {
      this.$router.push('/')
    },

    showError(message) {
      this.errorMessage = message
      setTimeout(() => {
        this.errorMessage = ''
      }, 5000)
    }
  }
}
</script>

<style scoped>
.admin-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Noto Sans KR', sans-serif;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.admin-header {
  background: white;
  padding: 20px 30px;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  margin-bottom: 25px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.admin-header h1 {
  color: #2c3e50;
  margin: 0;
  font-size: 1.8em;
}

.kiosk-btn {
  background: #28a745;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.kiosk-btn:hover {
  background: #218838;
  transform: translateY(-1px);
}

.stats-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 25px;
}

.stat-card {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-card h3 {
  color: #6c757d;
  font-size: 1em;
  margin: 0 0 15px 0;
  font-weight: 500;
}

.stat-value {
  color: #2c3e50;
  font-size: 2.5em;
  font-weight: bold;
  margin: 0;
}

.action-buttons {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  margin-bottom: 25px;
  display: flex;
  gap: 15px;
  justify-content: center;
}

.refresh-btn, .excel-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  min-width: 150px;
}

.refresh-btn {
  background: #007bff;
  color: white;
}

.refresh-btn:hover {
  background: #0056b3;
}

.excel-btn {
  background: #28a745;
  color: white;
}

.excel-btn:hover {
  background: #218838;
}

.refresh-btn:disabled, .excel-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
  transform: none;
}

/* 뷰 전환 탭 */
.view-tabs {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  margin-bottom: 25px;
  display: flex;
  gap: 10px;
  justify-content: center;
}

.view-tab {
  padding: 12px 24px;
  border: 2px solid #e0e6ed;
  background: white;
  cursor: pointer;
  border-radius: 25px;
  transition: all 0.3s;
  font-weight: 500;
  font-size: 16px;
}

.view-tab:hover {
  border-color: #007bff;
  background: #f8f9fa;
}

.view-tab.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

/* 고객별 주문 내역 섹션 */
.customers-section {
  background: white;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.customers-section h2 {
  color: #2c3e50;
  margin: 0 0 25px 0;
  font-size: 1.4em;
}

.customers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.customer-card {
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s;
}

.customer-card:hover {
  border-color: #007bff;
  box-shadow: 0 4px 15px rgba(0,123,255,0.1);
}

.customer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.customer-name {
  color: #2c3e50;
  font-size: 1.2em;
  margin: 0;
  font-weight: 600;
}

.customer-stats {
  display: flex;
  gap: 8px;
}

.stat-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  font-weight: 500;
}

.stat-badge.orders {
  background: #e3f2fd;
  color: #1565c0;
}

.stat-badge.items {
  background: #e8f5e8;
  color: #2e7d32;
}

.customer-info {
  margin-bottom: 15px;
}

.last-order {
  color: #6c757d;
  font-size: 0.9em;
}

.customer-orders h4 {
  color: #495057;
  font-size: 1em;
  margin: 0 0 10px 0;
}

.orders-summary {
  background: white;
  padding: 12px;
  border-radius: 8px;
  font-size: 0.9em;
  line-height: 1.4;
  color: #495057;
  border-left: 3px solid #007bff;
  max-height: 100px;
  overflow-y: auto;
}

.order-details {
  margin-top: 15px;
}

.toggle-details-btn {
  background: #6c757d;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.8em;
  cursor: pointer;
  transition: all 0.3s;
}

.toggle-details-btn:hover {
  background: #545b62;
}

.detailed-orders {
  margin-top: 15px;
  max-height: 300px;
  overflow-y: auto;
}

.order-detail-item {
  background: white;
  padding: 12px;
  margin: 8px 0;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.order-id {
  font-weight: 600;
  color: #495057;
  font-size: 0.9em;
}

.order-date {
  color: #6c757d;
  font-size: 0.8em;
  margin: 4px 0;
}

.order-items {
  margin-top: 8px;
}

.order-item {
  color: #495057;
  font-size: 0.85em;
  margin: 2px 0;
  padding-left: 8px;
}

/* 전체 주문 내역 섹션 */
.orders-section {
  background: white;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.orders-section h2 {
  color: #2c3e50;
  margin: 0 0 25px 0;
  font-size: 1.4em;
}

.loading-message, .empty-message {
  text-align: center;
  padding: 40px;
  color: #6c757d;
  font-size: 1.1em;
}

.orders-table-container {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.orders-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.orders-table th {
  background: #f8f9fa;
  color: #495057;
  font-weight: 600;
  padding: 15px 12px;
  text-align: left;
  border-bottom: 2px solid #dee2e6;
  white-space: nowrap;
}

.orders-table td {
  padding: 12px;
  border-bottom: 1px solid #e9ecef;
  vertical-align: top;
}

.orders-table tr:hover {
  background: #f8f9fa;
}

.even-row {
  background: #fafafa;
}

.text-center {
  text-align: center;
}

.customer-name {
  font-weight: 600;
  color: #2c3e50;
  min-width: 100px;
}

.order-content {
  max-width: 400px;
  word-wrap: break-word;
  line-height: 1.4;
}

.datetime {
  text-align: center;
}

.date {
  font-weight: 500;
  color: #495057;
}

.time {
  font-size: 0.9em;
  color: #6c757d;
  margin-top: 2px;
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
  .admin-container {
    padding: 10px;
  }
  
  .admin-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .admin-header h1 {
    font-size: 1.5em;
  }
  
  .stats-summary {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
  }
  
  .stat-value {
    font-size: 2em;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .action-buttons button {
    width: 100%;
    max-width: 300px;
  }
  
  .view-tabs {
    flex-direction: column;
    align-items: center;
  }
  
  .view-tabs button {
    width: 100%;
    max-width: 300px;
  }
  
  .customers-grid {
    grid-template-columns: 1fr;
  }
  
  .customer-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  
  .orders-table {
    font-size: 12px;
  }
  
  .orders-table th,
  .orders-table td {
    padding: 8px 6px;
  }
  
  .order-content {
    max-width: 200px;
    font-size: 12px;
  }
}
</style>
