import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { AuthProvider } from './contexts/AuthContext'
import { NotificationProvider } from './contexts/NotificationContext'
import { ToastProvider } from './contexts/ToastContext'
import { ConfirmProvider } from './contexts/ConfirmContext'
import ToastContainer from './components/ToastContainer'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <NotificationProvider>
        <ToastProvider>
          <ConfirmProvider>
            <App />
            <ToastContainer />
          </ConfirmProvider>
        </ToastProvider>
      </NotificationProvider>
    </AuthProvider>
  </StrictMode>,
)
