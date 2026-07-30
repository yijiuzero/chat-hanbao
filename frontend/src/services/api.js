import axios from 'axios'

const API_BASE = '/api'

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    console.error('[API Error]', message)
    return Promise.reject(new Error(message))
  }
)

// ============ 聊天 API ============
export const chatAPI = {
  send: (data) => apiClient.post('/chat/send', data),
  history: (sessionId) => apiClient.get(`/chat/history/${sessionId}`),
  clear: (sessionId) => apiClient.delete(`/chat/history/${sessionId}`),
}

// ============ 会话 API ============
export const sessionAPI = {
  create: (data) => apiClient.post('/sessions/create', data),
  list: (params) => apiClient.get('/sessions/list', { params }),
  get: (sessionId) => apiClient.get(`/sessions/${sessionId}`),
  delete: (sessionId) => apiClient.delete(`/sessions/${sessionId}`),
}

// ============ 健康检查 ============
export const healthAPI = {
  check: () => apiClient.get('/health'),
  dbCheck: () => apiClient.get('/health/db'),
}

export default apiClient
