import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { authApi } from '../utils/api';

const ForgotPassword = () => {
  const [step, setStep] = useState(1); // 1: email, 2: reset
  const [email, setEmail] = useState('');
  const [token, setToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await authApi.forgotPassword(email);
      setMessage(res.message);
      if (res.reset_token) {
        setToken(res.reset_token); // For testing - remove in production
        setStep(2);
      }
    } catch (err) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await authApi.resetPassword(email, token, newPassword);
      setMessage(res.message);
      setTimeout(() => {
        window.location.href = '/login';
      }, 2000);
    } catch (err) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-background">
      <div className="max-w-md w-full bg-card rounded-2xl shadow-2xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">PactAI</h1>
          <h2 className="text-2xl font-semibold text-foreground">
            {step === 1 ? 'Forgot Password' : 'Reset Password'}
          </h2>
        </div>

        {message && (
          <div className="mb-4 p-3 rounded-lg bg-blue-50 text-blue-700 text-sm">
            {message}
          </div>
        )}

        {step === 1 ? (
          <form onSubmit={handleForgotPassword} className="space-y-4">
            <div>
              <input
                type="email"
                required
                className="w-full px-4 py-3 border border-border rounded-lg bg-card placeholder-foreground text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                placeholder="Enter your email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-6 text-lg font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl shadow-lg hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Sending...' : 'Send Reset Instructions'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleResetPassword} className="space-y-4">
            <div>
              <input
                type="text"
                required
                className="w-full px-4 py-3 border border-border rounded-lg bg-card placeholder-foreground text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                placeholder="Reset token"
                value={token}
                onChange={(e) => setToken(e.target.value)}
              />
            </div>
            <div>
              <input
                type="password"
                required
                className="w-full px-4 py-3 border border-border rounded-lg bg-card placeholder-foreground text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                placeholder="New password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-6 text-lg font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl shadow-lg hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Resetting...' : 'Reset Password'}
            </button>
          </form>
        )}

        <div className="mt-6 text-center">
          <Link to="/login" className="text-primary hover:underline">
            Back to Login
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;