import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Chatbot from './pages/Chatbot';
import './globals.css';

// Create a component that conditionally renders Navbar and Footer
function Layout({ children }) {
  const location = useLocation();
  const isAuthPage = ['/login', '/signup'].includes(location.pathname);
  const isChatbotPage = location.pathname === '/chatbot'; // Check if it's chatbot page

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground transition-colors duration-300">
      {!isAuthPage && !isChatbotPage && <Navbar />} {/* Exclude navbar from chatbot */}
      <main className="flex-grow">
        {children}
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
        <Route path="/chatbot" element={<Chatbot />} /> Chatbot without Layout wrapper
        <Route path="*" element={
          <Layout>
            <Routes>
              <Route path="/" element={<Home />} />
            </Routes>
          </Layout>
        } />
      </Routes>
    </Router>
  );
}

export default App;