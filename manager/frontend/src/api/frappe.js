import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  baseURL: '/api/method/',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers['Authorization'] = `Bearer ${auth.token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 403) {
      const auth = useAuthStore()
      auth.clear()
    }
    return Promise.reject(error)
  }
)

export function frappeCall(method, params = {}) {
  return api.post(method, params).then((r) => r.data)
}

export function frappeGet(path, params = {}) {
  return api.get(path, { params }).then((r) => r.data)
}

export function createDoc(doctype, data) {
  return frappeCall('frappe.client.insert', { doc: { doctype, ...data } })
}

export function getDoc(doctype, name) {
  return frappeCall('frappe.client.get', { doctype, name })
}

export function updateDoc(doctype, name, data) {
  return frappeCall('frappe.client.set_value', { doctype, name, fieldname: data })
}

export function deleteDoc(doctype, name) {
  return frappeCall('frappe.client.delete', { doctype, name })
}

export function getList(doctype, filters = {}, fields = ['*'], limit = 100, orderBy = 'modified desc') {
  return frappeCall('frappe.client.get_list', { doctype, filters, fields, limit_page_length: limit, order_by: orderBy })
}

export default api
