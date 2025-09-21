import { BrowserRouter as Router, Routes, Route, useLocation, Outlet } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Chatbot from './pages/Chatbot';
import ForgotPassword from './pages/ForgotPassword';
import './globals.css';

// Create a component that conditionally renders Navbar and Footer
function Layout() {
  const location = useLocation();
  const isAuthPage = ['/login', '/signup', '/forgot-password'].includes(location.pathname);
  const isChatbotPage = location.pathname === '/chatbot'; // Check if it's chatbot page

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground transition-colors duration-300">
      {!isAuthPage && !isChatbotPage && <Navbar />} {/* Exclude navbar from chatbot */}
      <main className="flex-grow">
        <Outlet />
      </main>
      {!isAuthPage && !isChatbotPage && <Footer />} {/* Exclude footer from chatbot */}
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/chatbot" element={<Chatbot />} />
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;