import axios from 'axios'

console.log('API BASE URL:', import.meta.env.VITE_API_BASE_URL)

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export default http