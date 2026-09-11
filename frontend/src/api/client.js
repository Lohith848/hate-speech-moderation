import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

export const moderateText = async (text) => {
  const { data } = await client.post('/api/v1/moderate', { text })
  return data
}

export const moderateBatch = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await client.post('/api/v1/moderate/batch', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export const getStats = async (range = '7d') => {
  const { data } = await client.get(`/api/v1/stats?range=${range}`)
  return data
}

export default client
