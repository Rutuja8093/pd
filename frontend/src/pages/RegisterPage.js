import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from 'react-i18next';
import { Leaf, UserPlus, Eye, EyeOff } from 'lucide-react';
import { motion } from 'framer-motion';

export const RegisterPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await register(username, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F5F5F0] flex">
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        <img
          src="https://images.unsplash.com/photo-1678759916423-94a69a9dbcd0?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1OTV8MHwxfHNlYXJjaHwzfHxzdWdhcmNhbmUlMjBmaWVsZCUyMHBsYW50YXRpb24lMjBncmVlbnxlbnwwfHx8fDE3NzkzNDU0MzR8MA&ixlib=rb-4.1.0&q=85"
          alt="Sugarcane Field"
          className="absolute inset-0 w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-[#1A3626]/80 to-[#1A3626]/40" />
        <div className="relative z-10 flex flex-col justify-end p-12 text-white">
          <h2 className="text-3xl font-bold tracking-tight mb-3">Join SUGARCANE AI</h2>
          <p className="text-lg text-white/80 leading-relaxed max-w-md">
            Start detecting sugarcane diseases with AI-powered analysis and get expert-verified treatment plans.
          </p>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-6 sm:p-12">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md">
          <div className="lg:hidden flex items-center space-x-2.5 mb-10">
            <div className="w-10 h-10 bg-[#1A3626] rounded-lg flex items-center justify-center">
              <Leaf className="w-6 h-6 text-[#F5F5F0]" />
            </div>
            <span className="text-xl font-bold text-[#1A3626] tracking-tight">SUGARCANE<span className="text-[#839E88]"> AI</span></span>
          </div>

          <h1 className="text-4xl sm:text-5xl font-extrabold text-[#1A3626] tracking-tight mb-2">{t('register')}</h1>
          <p className="text-[#57695D] mb-8">Create your account to get started</p>

          {error && (
            <div className="bg-[#F5D0C9] border border-[#E29D90] text-[#8F2C1A] px-4 py-3 rounded-xl mb-6 text-sm font-medium">{error}</div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="text-xs uppercase tracking-[0.2em] text-[#839E88] font-semibold mb-2 block">{t('username')}</label>
              <input data-testid="register-username-input" type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Choose a username" required
                className="w-full bg-[#FDFDFB] border border-[#839E88]/40 rounded-lg px-4 py-3 focus:ring-2 focus:ring-[#1A3626] focus:border-transparent outline-none transition-all text-[#1A3626] placeholder:text-[#839E88]" />
            </div>
            <div>
              <label className="text-xs uppercase tracking-[0.2em] text-[#839E88] font-semibold mb-2 block">{t('password')}</label>
              <div className="relative">
                <input data-testid="register-password-input" type={showPw ? 'text' : 'password'} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Choose a password" required
                  className="w-full bg-[#FDFDFB] border border-[#839E88]/40 rounded-lg px-4 py-3 pr-12 focus:ring-2 focus:ring-[#1A3626] focus:border-transparent outline-none transition-all text-[#1A3626] placeholder:text-[#839E88]" />
                <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-[#839E88] hover:text-[#1A3626]">
                  {showPw ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>
            <button data-testid="register-submit-button" type="submit" disabled={loading}
              className="w-full bg-[#1A3626] text-[#FDFDFB] py-3.5 rounded-lg font-semibold text-base flex items-center justify-center space-x-2 transition-all hover:-translate-y-0.5 hover:shadow-lg hover:shadow-[#1A3626]/20 disabled:opacity-50 active:translate-y-0">
              {loading ? <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-[#FDFDFB]"></div> : <><UserPlus className="w-5 h-5" /><span>{t('registerButton')}</span></>}
            </button>
          </form>

          <p className="text-center text-[#57695D] mt-8 text-sm">
            {t('alreadyHaveAccount')}{' '}
            <Link to="/login" className="text-[#1A3626] font-semibold hover:underline underline-offset-4">{t('login')}</Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
};
