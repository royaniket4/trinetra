import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { authApi } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('trinetra_token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      authApi.getProfile()
        .then(res => setUser(res.data))
        .catch(() => {
          localStorage.removeItem('trinetra_token')
          setToken(null)
          setUser(null)
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [token])

  const login = useCallback(async (username, password) => {
    const res = await authApi.login(username, password)
    localStorage.setItem('trinetra_token', res.data.access_token)
    setToken(res.data.access_token)
    setUser(res.data.user)
    return res.data.user
  }, [])

  const register = useCallback(async (data) => {
    const res = await authApi.register(data)
    localStorage.setItem('trinetra_token', res.data.access_token)
    setToken(res.data.access_token)
    setUser(res.data.user)
    return res.data.user
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('trinetra_token')
    setToken(null)
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
