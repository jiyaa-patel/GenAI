import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Signup = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: ''
  });
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle signup logic here
    console.log('Signup form submitted:', formData);
    
    // Redirect to chatbot after successful signup
    navigate('/chatbot');
  };

  const handleGoogleSignup = (e) => {
    // Handle Google signup logic here
    console.log('Google signup clicked');
    // After successful Google signup, redirect to chatbot
    navigate('/chatbot');
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-4 px-4 sm:px-6 lg:px-8 bg-background">
      <div className="max-w-6xl w-full flex flex-col md:flex-row rounded-2xl overflow-hidden shadow-2xl">
        {/* Left side - Welcome content - Updated for dark theme */}
        <div className="w-full md:w-2/5 bg-gradient-to-br from-primary to-accent p-12 text-white flex flex-col justify-center">
          <h2 className="text-3xl font-bold mb-6">Welcome Back!</h2>
          <p className="mb-8 text-lg opacity-90">
            To keep connected with us please login with your personal info
          </p>
          <Link to="/login" className="mt-10 inline-block w-full">
            <button className="w-full py-3 px-4 rounded-lg text-gray-600 bg-white bg-opacity-20 hover:bg-opacity-30 transition-all duration-300 font-medium shadow-md hover:shadow-lg transform hover:-translate-y-0.5">
              SIGN IN
            </button>
          </Link>
        </div>

        {/* Right side - Form */}
        <div className="w-full md:w-3/5 bg-card p-12 flex flex-col justify-center">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-foreground mb-2">PactAI</h1>
            <h2 className="text-2xl font-semibold text-foreground">Create Account</h2>
          </div>

          {/* Social Login Buttons */}
          <div className="space-y-4 mb-6">
            <button 
              onClick={handleGoogleSignup}
              className="w-full flex items-center justify-center px-4 py-3 border border-border rounded-lg bg-card text-foreground hover:bg-gray-800 transition-all duration-300 shadow-sm hover:shadow-md font-medium"
            >
              <svg className="google-icon" viewBox="0 0 533.5 544.3" aria-hidden="true">
                <path fill="#4285f4" d="M533.5 278.4c0-18.5-1.5-36.2-4.4-53.4H272v101h146.9c-6.3 33.8-25 62.5-53.4 81.6v67.8h86.2c50.4-46.5 80.8-115.1 80.8-196z"/>
                <path fill="#34a853" d="M272 544.3c73.6 0 135.4-24.3 180.6-66l-86.2-67.8c-23.9 16.1-54.4 25.6-94.4 25.6-72.6 0-134.2-49.1-156.3-115.1H29.1v72.2C74.3 488.6 166 544.3 272 544.3z"/>
                <path fill="#fbbc04" d="M115.7 318.9c-10.6-31.8-10.6-66 0-97.8V149H29.1c-41.1 80.6-41.1 175.4 0 256l86.6-86.1z"/>
                <path fill="#ea4335" d="M272 109.1c39.6 0 75.2 13.6 103.2 40.3l77.4-77.4C407.4 24.4 345.6 0 272 0 166 0 74.3 55.7 29.1 149l86.6 72.2C137.8 158.2 199.4 109.1 272 109.1z"/>
              </svg>
              Continue with Google
            </button>
          </div>

          {/* Divider */}
          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-card text-foreground">
                or use your email for registration
              </span>
            </div>
          </div>

          {/* Registration Form */}
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <input
                id="name"
                name="name"
                type="text"
                autoComplete="name"
                required
                className="relative block w-full px-4 py-3 border border-border rounded-lg bg-card placeholder-foreground text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                placeholder="Name"
                value={formData.name}
                onChange={handleChange}
              />
            </div>
            <div>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="relative block w-full px-4 py-3 border border-border rounded-lg bg-card placeholder-foreground text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                placeholder="Email"
                value={formData.email}
                onChange={handleChange}
              />
            </div>
            <div>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                className="relative block w-full px-4 py-3 border border-border rounded-lg bg-card placeholder-foreground text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                placeholder="Password"
                value={formData.password}
                onChange={handleChange}
              />
            </div>

            <div>
              <button
                type="submit"
                className="w-full flex justify-center py-3.5 px-6 text-lg font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl shadow-lg hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-300 transform hover:-translate-y-0.5 hover:shadow-xl"
              >
                SIGN UP
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Signup;