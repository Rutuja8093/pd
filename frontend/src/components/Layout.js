import React, { useState, useRef, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from 'react-i18next';
import { LayoutDashboard, History, BookOpen, ShieldCheck, LogOut, Globe, ChevronDown, Leaf, Menu, X } from 'lucide-react';

export const Layout = ({ children }) => {
  const { user, logout } = useAuth();
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const [langOpen, setLangOpen] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const langRef = useRef(null);

  const isActive = (path) => location.pathname === path;

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (langRef.current && !langRef.current.contains(e.target)) setLangOpen(false);
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => { logout(); navigate('/login'); };

  const languages = [
    { code: 'en', label: 'English', short: 'EN' },
    { code: 'hi', label: 'हिन्दी', short: 'HI' },
    { code: 'mr', label: 'मराठी', short: 'MR' }
  ];

  const currentLang = languages.find(l => l.code === i18n.language) || languages[0];

  const navItems = [
    { path: '/dashboard', label: t('dashboard'), icon: LayoutDashboard, testId: 'nav-dashboard' },
    { path: '/history', label: t('history'), icon: History, testId: 'nav-history' },
    ...(user?.role === 'admin' ? [
      { path: '/diseases', label: t('diseases'), icon: BookOpen, testId: 'nav-diseases' },
      { path: '/admin', label: t('admin'), icon: ShieldCheck, testId: 'nav-admin' }
    ] : [])
  ];

  return (
    <div className="min-h-screen bg-[#F5F5F0]">
      {/* Glassmorphic Header */}
      <header className="bg-[#F5F5F0]/80 backdrop-blur-xl border-b border-[#1A3626]/10 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/dashboard" className="flex items-center space-x-2.5 group">
              <div className="w-9 h-9 bg-[#1A3626] rounded-lg flex items-center justify-center group-hover:scale-105 transition-transform">
                <Leaf className="w-5 h-5 text-[#F5F5F0]" />
              </div>
              <span className="text-lg font-bold text-[#1A3626] tracking-tight hidden sm:block">
                SUGARCANE<span className="text-[#839E88] font-medium"> AI</span>
              </span>
            </Link>

            {/* Desktop Nav */}
            <nav className="hidden md:flex items-center space-x-1">
              {navItems.map(item => (
                <Link
                  key={item.path}
                  to={item.path}
                  data-testid={item.testId}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive(item.path)
                      ? 'bg-[#1A3626] text-[#FDFDFB] shadow-md shadow-[#1A3626]/20'
                      : 'text-[#57695D] hover:bg-[#E8E8E3] hover:text-[#1A3626]'
                  }`}
                >
                  <item.icon className="w-4 h-4" strokeWidth={isActive(item.path) ? 2.5 : 1.5} />
                  <span>{item.label}</span>
                </Link>
              ))}
            </nav>

            {/* Right Side */}
            <div className="flex items-center space-x-3">
              {/* Language Toggle */}
              <div ref={langRef} className="relative">
                <button
                  data-testid="language-toggle-dropdown"
                  onClick={() => setLangOpen(!langOpen)}
                  className="flex items-center space-x-1.5 bg-[#E8E8E3] hover:bg-[#839E88]/30 px-3 py-1.5 rounded-full text-sm font-medium text-[#1A3626] transition-all"
                >
                  <Globe className="w-3.5 h-3.5" />
                  <span>{currentLang.short}</span>
                  <ChevronDown className={`w-3 h-3 transition-transform ${langOpen ? 'rotate-180' : ''}`} />
                </button>
                {langOpen && (
                  <div className="absolute right-0 mt-2 bg-[#FDFDFB] border border-[#1A3626]/10 rounded-xl shadow-xl py-1 min-w-[140px] z-50">
                    {languages.map(lang => (
                      <button
                        key={lang.code}
                        data-testid={`lang-${lang.code}`}
                        onClick={() => { i18n.changeLanguage(lang.code); setLangOpen(false); }}
                        className={`w-full px-4 py-2.5 text-left text-sm flex items-center justify-between transition-colors ${
                          i18n.language === lang.code ? 'bg-[#1A3626]/5 text-[#1A3626] font-semibold' : 'text-[#57695D] hover:bg-[#E8E8E3]'
                        }`}
                      >
                        <span>{lang.label}</span>
                        <span className="text-xs text-[#839E88]">{lang.short}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* User + Logout */}
              {user && (
                <div className="hidden sm:flex items-center space-x-3">
                  <div className="w-8 h-8 bg-[#839E88]/30 rounded-full flex items-center justify-center">
                    <span className="text-xs font-bold text-[#1A3626]">{user.username?.charAt(0).toUpperCase()}</span>
                  </div>
                  <button
                    data-testid="logout-btn"
                    onClick={handleLogout}
                    className="flex items-center space-x-1.5 text-sm text-[#57695D] hover:text-[#C25E4B] transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    <span>{t('logout')}</span>
                  </button>
                </div>
              )}

              {/* Mobile menu */}
              <button className="md:hidden p-2 rounded-lg hover:bg-[#E8E8E3]" onClick={() => setMobileOpen(!mobileOpen)}>
                {mobileOpen ? <X className="w-5 h-5 text-[#1A3626]" /> : <Menu className="w-5 h-5 text-[#1A3626]" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Nav */}
        {mobileOpen && (
          <div className="md:hidden border-t border-[#1A3626]/10 bg-[#FDFDFB] py-3 px-4 space-y-1">
            {navItems.map(item => (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setMobileOpen(false)}
                className={`flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium ${
                  isActive(item.path) ? 'bg-[#1A3626] text-[#FDFDFB]' : 'text-[#57695D] hover:bg-[#E8E8E3]'
                }`}
              >
                <item.icon className="w-4 h-4" />
                <span>{item.label}</span>
              </Link>
            ))}
            {user && (
              <button onClick={handleLogout} className="flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium text-[#C25E4B] hover:bg-[#F5D0C9]/30 w-full">
                <LogOut className="w-4 h-4" />
                <span>{t('logout')}</span>
              </button>
            )}
          </div>
        )}
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
};
