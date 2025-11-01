import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Box, Button, Typography } from '@mui/material'
import { useAuth } from '../hooks/useAuth'
import API from '../api'

import Summary from './asics/summary'

export default function Root() {
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const handleLogout = async () => {
    try {
      const api = new API()
      await api.POST({ path: '/logout' })
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      logout()
      navigate('/login')
    }
  }

  return (
    <div>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" component="h1">Hash for Heat</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="body2">Logged in as: {user?.username}</Typography>
          <Button variant="outlined" onClick={handleLogout}>Logout</Button>
        </Box>
      </Box>
      <Summary />      
    </div>
  )
}
