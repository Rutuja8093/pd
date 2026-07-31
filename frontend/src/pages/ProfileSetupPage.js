import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from 'react-i18next';
import { User, Phone } from '@phosphor-icons/react';
import { motion } from 'framer-motion';

export const ProfileSetupPage = () => {
  const [name, setName] = useState('');
  const [mobile, setMobile] = useState('');
  const [loading, setLoading] = useState(false);
  const { updateProfile } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await updateProfile(name, mobile);
      navigate('/dashboard');
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSkip = () => {
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F9F8F6] px-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md"
      >
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-[#1A201C]" style={{ fontFamily: 'Outfit, sans-serif' }}>
              {t('completeProfile')}
            </h1>
            <p className="text-[#5C6B61] mt-2">Help us know you better</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-[#1A201C] mb-2">
                {t('name')}
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 text-[#8B9D77]" size={20} />
                <input
                  id="name"
                  type="text"
                  data-testid="profile-name-input"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-[#DDE3DA] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2D5A27] focus:border-transparent"
                  placeholder="Enter your full name"
                  required
                />
              </div>
            </div>

            <div>
              <label htmlFor="mobile" className="block text-sm font-medium text-[#1A201C] mb-2">
                {t('mobile')}
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 text-[#8B9D77]" size={20} />
                <input
                  id="mobile"
                  type="tel"
                  data-testid="profile-mobile-input"
                  value={mobile}
                  onChange={(e) => setMobile(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-[#DDE3DA] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2D5A27] focus:border-transparent"
                  placeholder="Enter your mobile number"
                  required
                />
              </div>
            </div>

            <div className="flex space-x-4">
              <button
                type="button"
                onClick={handleSkip}
                className="flex-1 border border-[#DDE3DA] text-[#5C6B61] py-3 rounded-lg font-medium hover:bg-[#F9F8F6] transition-colors"
              >
                Skip for now
              </button>
              <button
                type="submit"
                data-testid="profile-save-button"
                disabled={loading}
                className="flex-1 bg-[#2D5A27] hover:bg-[#24481F] text-white py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
              >
                {loading ? t('loading') : t('saveProfile')}
              </button>
            </div>
          </form>
        </div>
      </motion.div>
    </div>
  );
};
