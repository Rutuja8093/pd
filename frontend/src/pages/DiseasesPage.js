import React, { useState, useEffect } from 'react';
import { Layout } from '../components/Layout';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Sprout, Wrench, Bug, FlaskConical, Clock, ChevronDown, Leaf, BookOpen } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const HERO_IMAGES = [
  "https://images.unsplash.com/photo-1668956342887-516a98c06889?crop=entropy&cs=srgb&fm=jpg&w=1200&q=80",
  "https://images.unsplash.com/photo-1724158126338-be1a7fa974a1?crop=entropy&cs=srgb&fm=jpg&w=1200&q=80",
  "https://images.pexels.com/photos/15876350/pexels-photo-15876350.jpeg?auto=compress&cs=tinysrgb&w=1200",
];

const PRACTICE_CONFIG = [
  { key: 'cultural_practices', icon: Sprout, title: 'Cultural Practices', titleMr: 'सांस्कृतिक पद्धती', titleHi: 'सांस्कृतिक प्रथाएं', gradient: 'from-[#1A3626] to-[#2D5A3E]' },
  { key: 'mechanical_practices', icon: Wrench, title: 'Mechanical Practices', titleMr: 'यांत्रिक पद्धती', titleHi: 'यांत्रिक प्रथाएं', gradient: 'from-[#57695D] to-[#6B8072]' },
  { key: 'biological_practices', icon: Bug, title: 'Biological Practices', titleMr: 'जैविक पद्धती', titleHi: 'जैविक प्रथाएं', gradient: 'from-[#839E88] to-[#9AB79F]' },
  { key: 'chemical_practices', icon: FlaskConical, title: 'Chemical Practices', titleMr: 'रासायनिक पद्धती', titleHi: 'रासायनिक प्रथाएं', gradient: 'from-[#C25E4B] to-[#D4776A]' },
  { key: 'spray_timing', icon: Clock, title: 'When & How to Spray', titleMr: 'फवारणी कधी व कशी', titleHi: 'कब और कैसे छिड़काव करें', gradient: 'from-[#B36B00] to-[#CC8A2E]' },
];

const PracticeSection = ({ config, items, lang, delay = 0 }) => {
  const [open, setOpen] = useState(false);
  if (!items || items.length === 0) return null;
  const Icon = config.icon;
  const title = lang === 'mr' ? config.titleMr : lang === 'hi' ? config.titleHi : config.title;

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }}>
      <button onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-4 rounded-xl bg-[#FDFDFB] border border-[#1A3626]/10 hover:shadow-md transition-all group">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${config.gradient} flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform`}>
            <Icon className="w-5 h-5 text-white" />
          </div>
          <span className="font-semibold text-[#1A3626] text-sm">{title}</span>
          <span className="text-xs text-[#839E88] bg-[#E8E8E3] px-2.5 py-0.5 rounded-full font-medium">{items.length}</span>
        </div>
        <ChevronDown className={`w-4 h-4 text-[#839E88] transition-transform duration-300 ${open ? 'rotate-180' : ''}`} />
      </button>
      <AnimatePresence>
        {open && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }} className="overflow-hidden">
            <div className="pt-2 pb-1 px-1 space-y-1.5">
              {items.map((item, i) => (
                <motion.div key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}
                  className="flex items-start gap-3 text-sm text-[#57695D] bg-[#F5F5F0] rounded-lg px-4 py-3 hover:bg-[#E8E8E3] transition-colors">
                  <div className={`w-2 h-2 rounded-full bg-gradient-to-br ${config.gradient} mt-1.5 flex-shrink-0`} />
                  <span className="leading-relaxed">{item}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export const DiseasesPage = () => {
  const [diseases, setDiseases] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedDisease, setSelectedDisease] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const { t, i18n } = useTranslation();

  useEffect(() => {
    fetchDiseases();
  }, [i18n.language]); // eslint-disable-line

  const fetchDiseases = async () => {
    try {
      const { data } = await axios.get(`${API_URL}/api/diseases?lang=${i18n.language}`);
      setDiseases(data);
      if (Object.keys(data).length > 0 && !selectedDisease) {
        setSelectedDisease(Object.keys(data)[0]);
      }
    } catch (error) {
      console.error('Failed to fetch diseases:', error);
    } finally {
      setLoading(false);
    }
  };

  const diseaseNames = Object.keys(diseases).filter(name =>
    name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (diseases[name]?.disease_name_local || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  const selected = selectedDisease && diseases[selectedDisease];

  return (
    <Layout>
      <motion.div data-testid="diseases-page" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        {/* Hero Banner */}
        <div className="relative rounded-2xl overflow-hidden mb-8 h-48 sm:h-56">
          <img
            src="https://images.unsplash.com/photo-1668956342887-516a98c06889?crop=entropy&cs=srgb&fm=jpg&w=1400&q=80"
            alt="Sugarcane Leaf"
            className="absolute inset-0 w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-[#1A3626]/90 via-[#1A3626]/70 to-transparent" />
          <div className="relative z-10 flex flex-col justify-center h-full px-8 sm:px-12">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-11 h-11 bg-white/15 backdrop-blur-md rounded-xl flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">{t('diseases')}</h1>
                <p className="text-sm text-white/70">23 diseases & pests</p>
              </div>
            </div>
            <p className="text-white/80 text-sm sm:text-base max-w-lg leading-relaxed">
              Complete management guide with cultural, mechanical, biological & chemical practices
            </p>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-16">
            <div className="animate-spin rounded-full h-10 w-10 border-t-3 border-[#1A3626] mx-auto"></div>
            <p className="mt-4 text-[#839E88]">{t('loading')}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Sidebar */}
            <div className="lg:col-span-4 xl:col-span-3">
              <div className="sticky top-24 space-y-3">
                <div className="relative">
                  <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#839E88]" />
                  <input type="text" placeholder={t('searchPlaceholder')} value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-[#FDFDFB] border border-[#839E88]/30 rounded-xl text-sm focus:ring-2 focus:ring-[#1A3626] focus:border-transparent outline-none text-[#1A3626] placeholder:text-[#839E88]" />
                </div>
                <div className="max-h-[60vh] overflow-y-auto space-y-1 pr-1 scrollbar-thin">
                  {diseaseNames.map((name, idx) => (
                    <motion.button
                      key={name}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.02 }}
                      onClick={() => setSelectedDisease(name)}
                      data-testid={`disease-card-${name.toLowerCase().replace(/\s+/g, '-')}`}
                      className={`w-full text-left px-4 py-3 rounded-xl text-sm transition-all ${
                        selectedDisease === name
                          ? 'bg-[#1A3626] text-[#FDFDFB] shadow-lg shadow-[#1A3626]/20 scale-[1.02]'
                          : 'bg-[#FDFDFB] text-[#1A3626] hover:bg-[#E8E8E3] border border-[#1A3626]/5 hover:border-[#1A3626]/20'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full flex-shrink-0 ${selectedDisease === name ? 'bg-white' : 'bg-[#839E88]'}`} />
                        <div>
                          <span className="font-medium block">{diseases[name]?.disease_name_local || name}</span>
                          {diseases[name]?.disease_name_local && diseases[name]?.disease_name_local !== name && (
                            <span className={`text-xs block mt-0.5 ${selectedDisease === name ? 'text-white/50' : 'text-[#839E88]'}`}>{name}</span>
                          )}
                        </div>
                      </div>
                    </motion.button>
                  ))}
                </div>
                <p className="text-xs text-[#839E88] text-center pt-2">{diseaseNames.length} diseases found</p>
              </div>
            </div>

            {/* Detail Panel */}
            <div className="lg:col-span-8 xl:col-span-9">
              <AnimatePresence mode="wait">
                {selected ? (
                  <motion.div key={selectedDisease} initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.3 }} className="space-y-6"
                  >
                    {/* Disease Header with decorative image */}
                    <div className="relative bg-[#FDFDFB] border border-[#1A3626]/10 rounded-2xl overflow-hidden">
                      <div className="absolute top-0 right-0 w-40 h-40 opacity-[0.06]">
                        <Leaf className="w-full h-full text-[#1A3626]" />
                      </div>
                      <div className="p-6 sm:p-8">
                        <div className="flex items-start gap-4">
                          <div className="w-14 h-14 bg-gradient-to-br from-[#1A3626] to-[#2D5A3E] rounded-2xl flex items-center justify-center flex-shrink-0 shadow-lg shadow-[#1A3626]/20">
                            <Leaf className="w-7 h-7 text-white" />
                          </div>
                          <div>
                            <h2 className="text-2xl sm:text-3xl font-extrabold text-[#1A3626] tracking-tight">
                              {selected.disease_name_local || selectedDisease}
                            </h2>
                            {selected.disease_name_local && selected.disease_name_local !== selectedDisease && (
                              <p className="text-sm text-[#839E88] mt-1">{selectedDisease}</p>
                            )}
                          </div>
                        </div>

                        {/* Info Cards */}
                        {selected.symptoms && (
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                            {[
                              { label: t('symptoms'), text: selected.symptoms, color: 'border-[#C25E4B]', bg: 'bg-[#C25E4B]/5' },
                              { label: t('causes'), text: selected.causes, color: 'border-[#B36B00]', bg: 'bg-[#B36B00]/5' },
                              { label: t('treatment'), text: selected.treatment, color: 'border-[#1A3626]', bg: 'bg-[#1A3626]/5' },
                              { label: t('prevention'), text: selected.prevention, color: 'border-[#839E88]', bg: 'bg-[#839E88]/10' },
                            ].filter(c => c.text).map((card, i) => (
                              <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}
                                className={`border-l-4 ${card.color} ${card.bg} rounded-r-xl pl-4 pr-4 py-3`}>
                                <h3 className="text-xs uppercase tracking-[0.15em] font-bold text-[#839E88] mb-1.5">{card.label}</h3>
                                <p className="text-sm text-[#57695D] leading-relaxed">{card.text}</p>
                              </motion.div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Practices Section */}
                    <div className="bg-[#FDFDFB] border border-[#1A3626]/10 rounded-2xl p-6 sm:p-8">
                      <div className="flex items-center gap-3 mb-5">
                        <div className="w-10 h-10 bg-[#E8E8E3] rounded-xl flex items-center justify-center">
                          <BookOpen className="w-5 h-5 text-[#1A3626]" />
                        </div>
                        <div>
                          <h3 className="text-lg font-bold text-[#1A3626]">
                            {i18n.language === 'mr' ? 'व्यवस्थापन पद्धती' : i18n.language === 'hi' ? 'प्रबंधन प्रथाएं' : 'Management Practices'}
                          </h3>
                          <p className="text-xs text-[#839E88]">
                            {i18n.language === 'mr' ? 'प्रत्येक विभाग विस्तारित करा' : i18n.language === 'hi' ? 'प्रत्येक अनुभाग विस्तृत करें' : 'Expand each section for detailed guidelines'}
                          </p>
                        </div>
                      </div>
                      <div className="space-y-3">
                        {PRACTICE_CONFIG.map((config, i) => (
                          <PracticeSection key={config.key} config={config} items={selected[config.key]} lang={i18n.language} delay={i * 0.06} />
                        ))}
                      </div>
                    </div>
                  </motion.div>
                ) : (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    className="bg-[#FDFDFB] border border-[#1A3626]/10 rounded-2xl p-16 text-center">
                    <Leaf className="w-16 h-16 mx-auto text-[#E8E8E3] mb-4" />
                    <p className="text-[#839E88]">Select a disease to view details</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        )}
      </motion.div>
    </Layout>
  );
};
