import React, { useState, useEffect } from 'react';
import { Layout } from '../components/Layout';
import { useTranslation } from 'react-i18next';
import { History, Search, Clock, CheckCircle2, XCircle, MessageSquare, ChevronDown, ChevronLeft, ChevronRight, Leaf, ShieldCheck, Pill, Bug, ShieldAlert, AlertTriangle, Sprout, Wrench, FlaskConical } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { format } from 'date-fns';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export const HistoryPage = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedId, setExpandedId] = useState(null);
  const [page, setPage] = useState(1); // 1 = cultural & mechanical, 2 = chemical & biological
  const { t, i18n } = useTranslation();

  const toggleExpanded = (id) => {
    if (expandedId === id) {
      setExpandedId(null);
    } else {
      setExpandedId(id);
      setPage(1);
    }
  };

  useEffect(() => { fetchHistory(); }, [i18n.language]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchHistory = async () => {
    try {
      const { data } = await axios.get(`${API_URL}/api/history?lang=${i18n.language}`, { withCredentials: true });
      setHistory(data);
    } catch (error) {
      console.error('Failed to fetch history:', error);
    } finally {
      setLoading(false);
    }
  };

  const statusConfig = {
    approved: { bg: 'bg-[#D7E8D6]', text: 'text-[#1A3626]', border: 'border-[#A3C4A5]', icon: CheckCircle2 },
    rejected: { bg: 'bg-[#F5D0C9]', text: 'text-[#8F2C1A]', border: 'border-[#E29D90]', icon: XCircle },
    pending: { bg: 'bg-[#FCE5CD]', text: 'text-[#B36B00]', border: 'border-[#F3C185]', icon: Clock }
  };

  const severityConfig = {
    high: 'bg-[#F5D0C9] text-[#8F2C1A] border-[#E29D90]',
    medium: 'bg-[#FCE5CD] text-[#B36B00] border-[#F3C185]',
    low: 'bg-[#D7E8D6] text-[#1A3626] border-[#A3C4A5]'
  };

  const filteredHistory = history.filter(item =>
    item.disease?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (item.status || 'pending').toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Layout>
      <motion.div data-testid="history-page" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-4xl sm:text-5xl font-extrabold text-[#1A3626] tracking-tight mb-1">{t('scanHistory')}</h1>
        <p className="text-base text-[#57695D] mb-8">{t('historySubtitle')}</p>

        <div className="mb-8">
          <div className="relative max-w-lg">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[#839E88]" />
            <input type="text" placeholder={t('searchPlaceholder')} value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-11 pr-4 py-3 bg-[#FDFDFB] border border-[#839E88]/40 rounded-xl focus:ring-2 focus:ring-[#1A3626] focus:border-transparent outline-none transition-all text-[#1A3626] placeholder:text-[#839E88]" />
          </div>
        </div>

        {loading ? (
          <div className="text-center py-16"><div className="animate-spin rounded-full h-10 w-10 border-t-3 border-[#1A3626] mx-auto"></div><p className="mt-4 text-[#839E88]">{t('loading')}</p></div>
        ) : filteredHistory.length === 0 ? (
          <div className="bg-[#FDFDFB] border border-[#1A3626]/10 rounded-2xl p-16 text-center">
            <History className="w-16 h-16 mx-auto text-[#E8E8E3] mb-4" strokeWidth={1} />
            <p className="text-[#839E88] text-lg">{t('noHistory')}</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredHistory.map((item, idx) => {
              const status = item.status || 'pending';
              const sc = statusConfig[status] || statusConfig.pending;
              const StatusIcon = sc.icon;
              const isExpanded = expandedId === item.id;

              return (
                <motion.div key={item.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.04 }}
                  data-testid={`history-item-${idx}`}
                  className="bg-[#FDFDFB] border border-[#1A3626]/10 rounded-xl overflow-hidden hover:shadow-md transition-shadow"
                >
                  <div className="p-5 cursor-pointer" onClick={() => toggleExpanded(item.id)}>
                    <div className="flex items-center gap-5">
                      <div className="flex gap-2 flex-shrink-0">
                        <div className="w-20 h-20 rounded-xl overflow-hidden bg-[#E8E8E3]">
                          <img src={`${API_URL}/api/files/${item.image_path}`} alt="" className="w-full h-full object-cover" />
                        </div>
                        {item.overlay_path && (
                          <div className="w-20 h-20 rounded-xl overflow-hidden bg-[#E8E8E3] relative">
                            <img src={`${API_URL}/api/files/${item.overlay_path}`} alt="AI Overlay" className="w-full h-full object-cover" />
                          </div>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            {item.disease === 'Unrecognized' ? (
                              <h3 className="text-lg font-bold text-[#B36B00] flex items-center gap-2">
                                <AlertTriangle className="w-5 h-5" />
                                {t('unrecognizedDisease')}
                              </h3>
                            ) : (
                              <h3 className="text-lg font-bold text-[#1A3626]">
                                {item.disease_name_local || item.disease}
                                {item.disease_name_local && item.disease_name_local !== item.disease && (
                                  <span className="text-sm font-normal text-[#839E88] ml-2">({item.disease})</span>
                                )}
                              </h3>
                            )}
                            <p className="text-xs text-[#839E88] mt-0.5">{format(new Date(item.created_at), 'PPpp')}</p>
                          </div>
                          <div className="flex items-center gap-2 flex-shrink-0">
                            {item.severity && (
                              <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border ${severityConfig[item.severity] || ''}`}>{item.severity}</span>
                            )}
                            <ChevronDown className={`w-4 h-4 text-[#839E88] transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                          </div>
                        </div>
                        {item.treatment && <p className="text-sm text-[#57695D] mt-1.5 line-clamp-1"><span className="font-medium text-[#1A3626]">{t('treatment')}:</span> {item.treatment}</p>}
                        {item.disease === 'Unrecognized' && <p className="text-sm text-[#B36B00] mt-1">{t('unrecognizedMsg')}</p>}
                      </div>
                    </div>
                  </div>

                  <AnimatePresence>
                    {isExpanded && item.disease !== 'Unrecognized' && (
                      <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.25 }}
                        className="border-t border-[#1A3626]/10 bg-[#F5F5F0] overflow-hidden"
                      >
                        <div className="p-6 space-y-5">
                          {/* Page indicator */}
                          <div className="flex items-center justify-center gap-2">
                            <span className={`w-2 h-2 rounded-full transition-colors ${page === 1 ? 'bg-[#1A3626]' : 'bg-[#839E88]/30'}`} />
                            <span className={`w-2 h-2 rounded-full transition-colors ${page === 2 ? 'bg-[#1A3626]' : 'bg-[#839E88]/30'}`} />
                          </div>

                          <AnimatePresence mode="wait">
                            {page === 1 && (
                              <motion.div key="page1" initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 12 }} transition={{ duration: 0.2 }} className="space-y-5">
                                {/* Disease identity + core info */}
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                                  <div className="space-y-1">
                                    <div className="flex items-center gap-2"><Bug className="w-4 h-4 text-[#C25E4B]" /><h4 className="text-xs uppercase tracking-[0.2em] font-bold text-[#839E88]">{t('symptoms')}</h4></div>
                                    <p className="text-sm text-[#57695D] leading-relaxed">{item.symptoms}</p>
                                  </div>
                                  <div className="space-y-1">
                                    <div className="flex items-center gap-2"><ShieldAlert className="w-4 h-4 text-[#B36B00]" /><h4 className="text-xs uppercase tracking-[0.2em] font-bold text-[#839E88]">{t('causes')}</h4></div>
                                    <p className="text-sm text-[#57695D] leading-relaxed">{item.causes}</p>
                                  </div>
                                  <div className="space-y-1">
                                    <div className="flex items-center gap-2"><Pill className="w-4 h-4 text-[#1A3626]" /><h4 className="text-xs uppercase tracking-[0.2em] font-bold text-[#839E88]">{t('treatment')}</h4></div>
                                    <p className="text-sm text-[#57695D] leading-relaxed">{item.treatment}</p>
                                  </div>
                                  <div className="space-y-1">
                                    <div className="flex items-center gap-2"><ShieldCheck className="w-4 h-4 text-[#839E88]" /><h4 className="text-xs uppercase tracking-[0.2em] font-bold text-[#839E88]">{t('prevention')}</h4></div>
                                    <p className="text-sm text-[#57695D] leading-relaxed">{item.prevention}</p>
                                  </div>
                                </div>

                                {item.admin_suggestion && (
                                  <div className="bg-[#FDFDFB] border-l-4 border-[#1A3626] rounded-r-xl p-4">
                                    <div className="flex items-center gap-2 mb-1.5"><MessageSquare className="w-4 h-4 text-[#1A3626]" /><h4 className="text-xs uppercase tracking-[0.2em] font-bold text-[#839E88]">{t('adminSuggestion')}</h4></div>
                                    <p className="text-sm text-[#57695D] leading-relaxed">{item.admin_suggestion}</p>
                                  </div>
                                )}

                                {/* Cultural & Mechanical practices */}
                                {(item.cultural_practices?.length > 0 || item.mechanical_practices?.length > 0) && (
                                  <div className="bg-[#FDFDFB] rounded-xl p-4 space-y-3">
                                    <h4 className="text-sm font-bold text-[#1A3626]">
                                      {t('managementPractices')}
                                    </h4>
                                    {[
                                      { items: item.cultural_practices, icon: Sprout, label: t('cultural'), color: 'text-[#1A3626]' },
                                      { items: item.mechanical_practices, icon: Wrench, label: t('mechanical'), color: 'text-[#57695D]' },
                                    ].filter(s => s.items?.length > 0).map((section, si) => (
                                      <div key={si}>
                                        <div className="flex items-center gap-1.5 mb-1">
                                          <section.icon className={`w-3.5 h-3.5 ${section.color}`} />
                                          <span className="text-xs font-bold text-[#839E88] uppercase tracking-wider">{section.label}</span>
                                        </div>
                                        <ul className="space-y-1 pl-5">
                                          {section.items.map((p, pi) => (
                                            <li key={pi} className="text-xs text-[#57695D] leading-relaxed list-disc">{p}</li>
                                          ))}
                                        </ul>
                                      </div>
                                    ))}
                                  </div>
                                )}
                              </motion.div>
                            )}

                            {page === 2 && (
                              <motion.div key="page2" initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -12 }} transition={{ duration: 0.2 }} className="space-y-5">
                                {/* Chemical practices - structured dosage table if available */}
                                {(item.chemical_reference?.length > 0 || item.chemical_practices?.length > 0) && (
                                  <div className="bg-[#FDFDFB] rounded-xl p-4 space-y-3">
                                    <div className="flex items-center gap-1.5">
                                      <FlaskConical className="w-4 h-4 text-[#C25E4B]" />
                                      <h4 className="text-sm font-bold text-[#1A3626]">
                                        {t('chemicalPractices')}
                                      </h4>
                                    </div>

                                    {item.chemical_reference?.length > 0 ? (
                                      <div className="overflow-x-auto">
                                        <table className="w-full text-xs">
                                          <thead>
                                            <tr className="text-left text-[#839E88] uppercase tracking-wider">
                                              <th className="pb-2 pr-3 font-bold">{t('product')}</th>
                                              <th className="pb-2 pr-3 font-bold">{t('dosage')}</th>
                                              <th className="pb-2 font-bold">{t('fracGroup')}</th>
                                            </tr>
                                          </thead>
                                          <tbody>
                                            {item.chemical_reference.map((row, ri) => (
                                              <tr key={ri} className="border-t border-[#E8E8E3]">
                                                <td className="py-2 pr-3 text-[#1A3626] font-medium">{row.product}</td>
                                                <td className="py-2 pr-3 text-[#57695D]">{row.dosage}</td>
                                                <td className="py-2 text-[#57695D]">{row.group}</td>
                                              </tr>
                                            ))}
                                          </tbody>
                                        </table>
                                      </div>
                                    ) : (
                                      <ul className="space-y-1 pl-5">
                                        {item.chemical_practices.map((p, pi) => (
                                          <li key={pi} className="text-xs text-[#57695D] leading-relaxed list-disc">{p}</li>
                                        ))}
                                      </ul>
                                    )}

                                    {item.spray_timing?.length > 0 && (
                                      <div className="pt-2">
                                        <div className="flex items-center gap-1.5 mb-1">
                                          <Clock className="w-3.5 h-3.5 text-[#B36B00]" />
                                          <span className="text-xs font-bold text-[#839E88] uppercase tracking-wider">
                                            {t('sprayTiming')}
                                          </span>
                                        </div>
                                        <ul className="space-y-1 pl-5">
                                          {item.spray_timing.map((p, pi) => (
                                            <li key={pi} className="text-xs text-[#57695D] leading-relaxed list-disc">{p}</li>
                                          ))}
                                        </ul>
                                      </div>
                                    )}
                                  </div>
                                )}

                                {/* Biological practices */}
                                {item.biological_practices?.length > 0 && (
                                  <div className="bg-[#FDFDFB] rounded-xl p-4 space-y-2">
                                    <div className="flex items-center gap-1.5">
                                      <Bug className="w-4 h-4 text-[#839E88]" />
                                      <h4 className="text-sm font-bold text-[#1A3626]">
                                        {t('biologicalPractices')}
                                      </h4>
                                    </div>
                                    <ul className="space-y-1 pl-5">
                                      {item.biological_practices.map((p, pi) => (
                                        <li key={pi} className="text-xs text-[#57695D] leading-relaxed list-disc">{p}</li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                              </motion.div>
                            )}
                          </AnimatePresence>

                          {/* Pagination controls */}
                          <div className="flex items-center justify-between pt-1">
                            <button
                              type="button"
                              onClick={(e) => { e.stopPropagation(); setPage(1); }}
                              disabled={page === 1}
                              className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                                page === 1 ? 'opacity-0 pointer-events-none' : 'bg-[#FDFDFB] text-[#1A3626] border border-[#1A3626]/15 hover:bg-[#E8E8E3]'
                              }`}
                            >
                              <ChevronLeft className="w-3.5 h-3.5" />
                              {t('back')}
                            </button>
                            <button
                              type="button"
                              onClick={(e) => { e.stopPropagation(); setPage(2); }}
                              disabled={page === 2}
                              className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                                page === 2 ? 'opacity-0 pointer-events-none' : 'bg-[#1A3626] text-white hover:bg-[#2D5A3E] shadow-sm'
                              }`}
                            >
                              {t('next')}
                              <ChevronRight className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </div>
                      </motion.div>
                    )}
                    {isExpanded && status === 'rejected' && item.admin_suggestion && (
                      <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}
                        className="border-t border-[#E29D90] bg-[#F5D0C9]/30 overflow-hidden"
                      >
                        <div className="p-5">
                          <div className="flex items-center gap-2 mb-1.5"><MessageSquare className="w-4 h-4 text-[#8F2C1A]" /><h4 className="text-xs uppercase tracking-[0.2em] font-bold text-[#8F2C1A]">{t('adminNote')}</h4></div>
                          <p className="text-sm text-[#57695D]">{item.admin_suggestion}</p>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              );
            })}
          </div>
        )}
      </motion.div>
    </Layout>
  );
};
