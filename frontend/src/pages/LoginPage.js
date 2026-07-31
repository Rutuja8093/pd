import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from 'react-i18next';
import { Leaf, LogIn, Eye, EyeOff } from 'lucide-react';
import { motion } from 'framer-motion';

export const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await login(username, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F5F5F0] flex">
      {/* Left - Hero Image */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        <img
          src="https://images.pexels.com/photos/11466855/pexels-photo-11466855.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=1200&w=800"
          alt="Sugarcane Field"
          className="absolute inset-0 w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-[#1A3626]/80 to-[#1A3626]/40" />
        <div className="relative z-10 flex flex-col justify-end p-12 text-white">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-12 h-12 bg-white/20 backdrop-blur-md rounded-xl flex items-center justify-center">
              <Leaf className="w-7 h-7 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold tracking-tight">SUGARCANE AI</h2>
              <p className="text-sm text-white/70">Smart Disease Detection</p>
            </div>
          </div>
          <p className="text-lg text-white/80 leading-relaxed max-w-md">
            AI-powered sugarcane disease analysis with expert-verified results and actionable treatment recommendations.
          </p>
        </div>
      </div>

      {/* Right - Form */}
      <div className="flex-1 flex items-center justify-center p-6 sm:p-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md"
        >
          {/* Mobile Logo */}
          <div className="lg:hidden flex items-center space-x-2.5 mb-10">
            <div className="w-10 h-10 bg-[#1A3626] rounded-lg flex items-center justify-center">
              <Leaf className="w-6 h-6 text-[#F5F5F0]" />
            </div>
            <span className="text-xl font-bold text-[#1A3626] tracking-tight">
              SUGARCANE<span className="text-[#839E88]"> AI</span>
            </span>
          </div>

          <h1 className="text-4xl sm:text-5xl font-extrabold text-[#1A3626] tracking-tight mb-2">
            {t('login')}
          </h1>
          <p className="text-[#57695D] mb-8">Sign in to access your dashboard</p>

          {error && (
            <div className="bg-[#F5D0C9] border border-[#E29D90] text-[#8F2C1A] px-4 py-3 rounded-xl mb-6 text-sm font-medium">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="text-xs uppercase tracking-[0.2em] text-[#839E88] font-semibold mb-2 block">{t('username')}</label>
              <input
                data-testid="login-email-input"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter username"
                required
                className="w-full bg-[#FDFDFB] border border-[#839E88]/40 rounded-lg px-4 py-3 focus:ring-2 focus:ring-[#1A3626] focus:border-transparent outline-none transition-all text-[#1A3626] placeholder:text-[#839E88]"
              />
            </div>
            <div>
              <label className="text-xs uppercase tracking-[0.2em] text-[#839E88] font-semibold mb-2 block">{t('password')}</label>
              <div className="relative">
                <input
                  data-testid="login-password-input"
                  type={showPw ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter password"
                  required
                  className="w-full bg-[#FDFDFB] border border-[#839E88]/40 rounded-lg px-4 py-3 pr-12 focus:ring-2 focus:ring-[#1A3626] focus:border-transparent outline-none transition-all text-[#1A3626] placeholder:text-[#839E88]"
                />
                <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-[#839E88] hover:text-[#1A3626]">
                  {showPw ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>
            <button
              data-testid="login-submit-button"
              type="submit"
              disabled={loading}
              className="w-full bg-[#1A3626] text-[#FDFDFB] py-3.5 rounded-lg font-semibold text-base flex items-center justify-center space-x-2 transition-all hover:-translate-y-0.5 hover:shadow-lg hover:shadow-[#1A3626]/20 disabled:opacity-50 disabled:hover:translate-y-0 disabled:hover:shadow-none active:translate-y-0"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-[#FDFDFB]"></div>
              ) : (
                <>
                  <LogIn className="w-5 h-5" />
                  <span>{t('loginButton')}</span>
                </>
              )}
            </button>
          </form>

          <p className="text-center text-[#57695D] mt-8 text-sm">
            {t('dontHaveAccount')}{' '}
            <Link data-testid="register-form-link" to="/register" className="text-[#1A3626] font-semibold hover:underline underline-offset-4">
              {t('register')}
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
};
