import { createRoot } from 'react-dom/client'
import './global.scss';
import { BrowserRouter } from 'react-router-dom'
import LandingPage from './LandingPage.jsx'

createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <LandingPage />
  </BrowserRouter>
)
