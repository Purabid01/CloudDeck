import { createContext, useContext, useState } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [member, setMember] = useState(() => {
    // check if already logged in from previous session
    const token = localStorage.getItem('access_token')
    const memberData = localStorage.getItem('member')
    if (token && memberData) {
      return JSON.parse(memberData)
    }
    return null
  })

  const loginSuccess = (token, memberData) => {
    localStorage.setItem('access_token', token)
    localStorage.setItem('member', JSON.stringify(memberData))
    setMember(memberData)
  }

  const logoutMember = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('member')
    setMember(null)
  }

  return (
    <AuthContext.Provider value={{ member, loginSuccess, logoutMember }}>
      {children}
    </AuthContext.Provider>
  )
}

// custom hook — any component calls useAuth() to get member info
export function useAuth() {
  return useContext(AuthContext)
}