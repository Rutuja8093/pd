import React, { useState, useEffect } from 'react';
import { Layout } from '../components/Layout';
import { useTranslation } from 'react-i18next';
import {
  Users, ScanLine, PieChart, Clock, Download, CheckCircle2,
  ChevronDown, Bug, ShieldCheck, Pill, ShieldAlert,
  MessageSquare, Sprout, Wrench, FlaskConical, Search,
  Filter, AlertTriangle, ArrowRight, X, Send
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { format } from 'date-fns';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export const AdminPage = () => {
  const { t, i18n } = useTranslation();
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [detections, setDetections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('scans'); // 'scans', 'farmers', 'overview'
  const [downloading, setDownloading] = useState(false);

  // Filters for All Scans
  const [searchQuery, setSearchQuery] = useState('');
  const [advisoryFilter, setAdvisoryFilter] = useState('all'); // 'all', 'needs_advisory', 'has_advisory'
  const [selectedFarmer, setSelectedFarmer] = useState(null);

  // Advisory Editing state
  const [editingAdvisoryId, setEditingAdvisoryId] = useState(null);
  const [advisoryText, setAdvisoryText] = useState('');
  const [savingAdvisory, setSavingAdvisory] = useState(false);

  // Expanded card details
  const [expandedScanId, setExpandedScanId] = useState(null);

  useEffect(() => {
    fetchData();
  }, [i18n.language]);

  const fetchData = async () => {
    try {
      const currentLang = i18n.language || 'en';
      const [statsRes, usersRes, detectionsRes] = await Promise.all([
        axios.get(`${API_URL}/api/admin/stats`, { withCredentials: true }),
        axios.get(`${API_URL}/api/admin/users`, { withCredentials: true }),
        axios.get(`${API_URL}/api/admin/detections?lang=${currentLang}`, { withCredentials: true }),
      ]);
      setStats(statsRes.data);
      setUsers(usersRes.data);
      setDetections(detectionsRes.data);
    } catch (error) {
      console.error('Failed to fetch admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveAdvisory = async (detectionId) => {
    if (!advisoryText.trim()) return;
    setSavingAdvisory(true);
    try {
      await axios.post(
        `${API_URL}/api/admin/advisory/${detectionId}`,
        { action: 'advisory', suggestion: advisoryText.trim() },
        { withCredentials: true }
      );
      setDetections((prev) =>
        prev.map((d) =>
          d.id === detectionId
            ? {
                ...d,
                admin_suggestion: advisoryText.trim(),
                reviewed_by: 'Admin Expert',
                reviewed_at: new Date().toISOString(),
              }
            : d
        )
      );
      setEditingAdvisoryId(null);
      setAdvisoryText('');
    } catch (e) {
      alert('Failed to save advisory.');
    } finally {
      setSavingAdvisory(false);
    }
  };

  const openAdvisoryEditor = (item) => {
    setEditingAdvisoryId(item.id);
    setAdvisoryText(item.admin_suggestion || '');
  };

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const res = await axios.get(`${API_URL}/api/admin/download-images`, {
        withCredentials: true,
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement('a');
      a.href = url;
      a.setAttribute('download', `sugarcane_scans_${new Date().toISOString().slice(0, 10)}.zip`);
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      alert(e.response?.status === 404 ? 'No images found.' : 'Download failed.');
    } finally {
      setDownloading(false);
    }
  };

  const handleViewFarmerScans = (username) => {
    setSelectedFarmer(username);
    setActiveTab('scans');
  };

  const severityColor = (s) =>
    ({
      high: 'bg-[#F5D0C9] text-[#8F2C1A] border-[#E29D90]',
      medium: 'bg-[#FCE5CD] text-[#B36B00] border-[#F3C185]',
      low: 'bg-[#D7E8D6] text-[#1A3626] border-[#A3C4A5]',
    }[s] || 'bg-[#E8E8E3] text-[#57695D] border-[#1A3626]/10');

  // Filtered detections
  const filteredDetections = detections.filter((d) => {
    if (selectedFarmer && d.username !== selectedFarmer) return false;
    if (advisoryFilter === 'needs_advisory' && d.admin_suggestion) return false;
    if (advisoryFilter === 'has_advisory' && !d.admin_suggestion) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matchUser = (d.username || '').toLowerCase().includes(q);
      const matchDisease =
        (d.disease || '').toLowerCase().includes(q) ||
        (d.disease_name_local || '').toLowerCase().includes(q);
      if (!matchUser && !matchDisease) return false;
    }
    return true;
  });

  const tabs = [
    { id: 'scans', label: `${t('allScans')} (${detections.length})`, icon: ScanLine },
    { id: 'farmers', label: `${t('registeredFarmers')} (${users.length})`, icon: Users },
    { id: 'overview', label: t('overview'), icon: PieChart },
  ];

  return (
    <Layout>
      <motion.div
        data-testid="admin-page"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6"
      >
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-[#1A3626] tracking-tight">
              {t('admin')}
            </h1>
            <p className="text-sm sm:text-base text-[#57695D] mt-1">
              {t('adminSubtitle')}
            </p>
          </div>
          <button
            data-testid="admin-download-zip-button"
            onClick={handleDownload}
            disabled={downloading}
            className="bg-[#1A3626] text-[#FDFDFB] px-5 py-2.5 rounded-xl font-semibold flex items-center justify-center space-x-2 transition-all hover:-translate-y-0.5 hover:shadow-lg hover:shadow-[#1A3626]/20 disabled:opacity-50 text-sm"
          >
            {downloading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-white"></div>
                <span>{t('preparing')}</span>
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                <span>{t('downloadImagesZip')}</span>
              </>
            )}
          </button>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: t('totalScans'), value: stats?.total_scans || detections.length, icon: ScanLine, color: '#1A3626', bg: '#E8E8E3' },
            { label: t('registeredFarmers'), value: stats?.total_users || users.length, icon: Users, color: '#1A3626', bg: '#E8E8E3' },
            {
              label: t('needsAdvisory'),
              value: detections.filter((d) => !d.admin_suggestion).length,
              icon: Clock,
              color: '#B36B00',
              bg: '#FCE5CD',
            },
            {
              label: t('hasAdvisory'),
              value: detections.filter((d) => !!d.admin_suggestion).length,
              icon: MessageSquare,
              color: '#1A3626',
              bg: '#D7E8D6',
            },
          ].map((s, i) => (
            <div
              key={i}
              className="bg-[#FDFDFB] border border-[#1A3626]/10 rounded-2xl p-5 shadow-[4px_4px_10px_rgba(26,54,38,0.05),-4px_-4px_10px_rgba(255,255,255,1)]"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-[11px] uppercase tracking-wider font-bold text-[#839E88]">{s.label}</p>
                  <p className="text-3xl font-extrabold text-[#1A3626] mt-1">{s.value}</p>
                </div>
                <div className="w-11 h-11 rounded-xl flex items-center justify-center" style={{ backgroundColor: s.bg }}>
                  <s.icon className="w-5 h-5" style={{ color: s.color }} />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Navigation Tabs */}
        <div className="flex space-x-2 border-b border-[#1A3626]/10 pb-px">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`pb-3 px-5 text-sm font-bold flex items-center gap-2 transition-all ${
                  isActive
                    ? 'text-[#1A3626] border-b-2 border-[#1A3626]'
                    : 'text-[#839E88] hover:text-[#1A3626]'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {loading ? (
          <div className="text-center py-16">
            <div className="animate-spin rounded-full h-10 w-10 border-t-3 border-[#1A3626] mx-auto"></div>
          </div>
        ) : (
          <>
            {/* 1. ALL SCANS TAB */}
            {activeTab === 'scans' && (
              <div className="space-y-5">
                {/* Filter and Search Bar */}
                <div className="bg-[#FDFDFB] border border-[#1A3626]/10 rounded-2xl p-4 shadow-xs flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
                  <div className="relative flex-1">
                    <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#839E88]" />
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder={t('searchPlaceholder')}
                      className="w-full bg-[#F5F5F0] border border-[#1A3626]/10 rounded-xl pl-10 pr-4 py-2 text-sm text-[#1A3626] placeholder-[#839E88] focus:ring-2 focus:ring-[#1A3626] outline-none"
                    />
                  </div>

                  <div className="flex flex-wrap items-center gap-2">
                    <div className="flex items-center gap-1 bg-[#F5F5F0] p-1 rounded-xl border border-[#1A3626]/10 text-xs font-bold">
                      <button
                        onClick={() => setAdvisoryFilter('all')}
                        className={`px-3 py-1.5 rounded-lg transition-all ${
                          advisoryFilter === 'all' ? 'bg-[#1A3626] text-white shadow-xs' : 'text-[#57695D] hover:text-[#1A3626]'
                        }`}
                      >
                        {t('all')}
                      </button>
                      <button
                        onClick={() => setAdvisoryFilter('needs_advisory')}
                        className={`px-3 py-1.5 rounded-lg transition-all ${
                          advisoryFilter === 'needs_advisory' ? 'bg-[#B36B00] text-white shadow-xs' : 'text-[#57695D] hover:text-[#1A3626]'
                        }`}
                      >
                        {t('needsAdvisory')}
                      </button>
                      <button
                        onClick={() => setAdvisoryFilter('has_advisory')}
                        className={`px-3 py-1.5 rounded-lg transition-all ${
                          advisoryFilter === 'has_advisory' ? 'bg-[#1A3626] text-white shadow-xs' : 'text-[#57695D] hover:text-[#1A3626]'
                        }`}
                      >
                        {t('hasAdvisory')}
                      </button>
                    </div>

                    {selectedFarmer && (
                      <div className="flex items-center gap-1.5 bg-[#D7E8D6] text-[#1A3626] border border-[#A3C4A5] px-3 py-1.5 rounded-xl text-xs font-bold">
                        <span>{t('showingScansFor')}: <span className="underline">{selectedFarmer}</span></span>
                        <button onClick={() => setSelectedFarmer(null)} className="p-0.5 hover:bg-[#1A3626]/10 rounded-full">
                          <X className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {/* Scans List */}
                {filteredDetections.length === 0 ? (
                  <div className="bg-[#FDFDFB] border border-[#1A3626]/10 rounded-2xl p-16 text-center">
                    <ScanLine className="w-14 h-14 mx-auto text-[#839E88]/40 mb-3" strokeWidth={1.5} />
                    <p className="text-base font-bold text-[#1A3626]">{t('noScansFound')}</p>
                    {selectedFarmer && (
                      <button
                        onClick={() => setSelectedFarmer(null)}
                        className="mt-3 text-sm text-[#1A3626] font-semibold underline"
                      >
                        {t('clearFilter')}
                      </button>
                    )}
                  </div>
                ) : (
                  <div className="space-y-4">
                    {filteredDetections.map((item) => {
                      const isExpanded = expandedScanId === item.id;
                      const isEditingAdvisory = editingAdvisoryId === item.id;
                      return (
                        <div
                          key={item.id}
                          className="bg-[#FDFDFB] border border-[#1A3626]/10 rounded-2xl overflow-hidden shadow-[4px_4px_10px_rgba(26,54,38,0.03)]"
                        >
                          <div className="p-5 sm:p-6">
                            <div className="flex flex-col md:flex-row gap-5">
                              {/* Scan Thumbnails */}
                              <div className="flex gap-2 flex-shrink-0">
                                <div className="w-32 h-32 rounded-xl overflow-hidden bg-[#E8E8E3] relative">
                                  <img
                                    src={`${API_URL}/api/files/${item.image_path}`}
                                    alt="Original Scan"
                                    className="w-full h-full object-cover"
                                  />
                                  <span className="absolute bottom-1 left-1 bg-black/60 text-white text-[9px] font-bold px-1.5 py-0.5 rounded">
                                    Original
                                  </span>
                                </div>
                                {item.overlay_path && item.disease !== 'Unrecognized' && (
                                  <div className="w-32 h-32 rounded-xl overflow-hidden bg-[#E8E8E3] relative">
                                    <img
                                      src={`${API_URL}/api/files/${item.overlay_path}`}
                                      alt="AI Segmentation"
                                      className="w-full h-full object-cover"
                                    />
                                    <span className="absolute bottom-1 left-1 bg-[#1A3626]/80 text-white text-[9px] font-bold px-1.5 py-0.5 rounded">
                                      AI Mask
                                    </span>
                                  </div>
                                )}
                              </div>

                              {/* Details */}
                              <div className="flex-1 min-w-0 flex flex-col justify-between">
                                <div>
                                  <div className="flex items-start justify-between gap-2 mb-2">
                                    <div>
                                      <p className="text-sm font-bold text-[#1A3626] flex items-center gap-1.5">
                                        <span>{t('farmer')}:</span>
                                        <button
                                          onClick={() => handleViewFarmerScans(item.username)}
                                          className="text-[#1A3626] underline hover:text-[#839E88] transition-colors"
                                        >
                                          {item.username}
                                        </button>
                                      </p>
                                      <p className="text-xs text-[#839E88] mt-0.5">
                                        {format(new Date(item.created_at), 'PPpp')}
                                      </p>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      {item.disease === 'Unrecognized' ? (
                                        <span className="px-3 py-1 rounded-full text-xs font-bold bg-[#FCE5CD] text-[#B36B00] border border-[#F3C185]">
                                          {t('notSupported')}
                                        </span>
                                      ) : (
                                        <span className={`px-3 py-1 rounded-full text-xs font-bold border ${severityColor(item.severity)}`}>
                                          {item.severity}
                                        </span>
                                      )}
                                    </div>
                                  </div>

                                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                                    <h3 className="text-xl font-extrabold text-[#1A3626]">
                                      {item.disease === 'Unrecognized' ? t('unrecognizedDisease') : (item.disease_name_local || item.disease)}
                                    </h3>
                                    {item.disease !== 'Unrecognized' && item.disease_name_local && item.disease_name_local !== item.disease && (
                                      <span className="text-xs text-[#839E88] font-semibold">({item.disease})</span>
                                    )}
                                    {item.is_co_infection && (
                                      <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-[#FCE5CD] text-[#B36B00] border border-[#F3C185]">
                                        {t('dualDetection')}
                                      </span>
                                    )}
                                  </div>

                                  {/* Multi-model AI breakdown */}
                                  {item.disease !== 'Unrecognized' && item.ai_predictions && item.ai_predictions.length > 1 && (
                                    <div className="flex flex-wrap gap-2 mb-3">
                                      {item.ai_predictions.map((p, idx) => (
                                        <div
                                          key={idx}
                                          className="bg-[#F5F5F0] border border-[#1A3626]/10 rounded-lg px-2.5 py-1 flex items-center gap-2 text-xs"
                                        >
                                          <span
                                            className="w-2 h-2 rounded-full flex-shrink-0"
                                            style={{
                                              backgroundColor:
                                                p.disease === 'Red Rot'
                                                  ? '#DC2626'
                                                  : p.disease === 'Brown Rust'
                                                  ? '#EA580C'
                                                  : '#84CC16',
                                            }}
                                          ></span>
                                          <span className="font-bold text-[#1A3626]">{p.disease}</span>
                                          <span className="font-semibold text-[#57695D]">
                                            {Math.round((p.confidence || 0) * 100)}%
                                          </span>
                                        </div>
                                      ))}
                                    </div>
                                  )}
                                </div>

                                {/* Expert Advisory Banner / Form */}
                                <div className="mt-3 pt-3 border-t border-[#1A3626]/10">
                                  {item.admin_suggestion && !isEditingAdvisory ? (
                                    <div className="bg-[#D7E8D6]/70 border border-[#A3C4A5] rounded-xl p-3.5 flex items-start justify-between gap-3">
                                      <div className="flex items-start gap-2.5">
                                        <MessageSquare className="w-5 h-5 text-[#1A3626] flex-shrink-0 mt-0.5" />
                                        <div>
                                          <div className="flex items-center gap-2">
                                            <span className="text-[11px] font-extrabold uppercase tracking-wider text-[#1A3626]">
                                              {t('expertAdvisory')}
                                            </span>
                                            {item.reviewed_at && (
                                              <span className="text-[10px] text-[#57695D]">
                                                • {format(new Date(item.reviewed_at), 'PP p')}
                                              </span>
                                            )}
                                          </div>
                                          <p className="text-sm text-[#1A3626] font-medium mt-1 leading-relaxed">
                                            {item.admin_suggestion}
                                          </p>
                                        </div>
                                      </div>
                                      <button
                                        onClick={() => openAdvisoryEditor(item)}
                                        className="text-xs font-bold text-[#1A3626] hover:underline flex-shrink-0"
                                      >
                                        {t('editAdvisory')}
                                      </button>
                                    </div>
                                  ) : !isEditingAdvisory ? (
                                    <div className="flex items-center justify-between">
                                      <span className="text-xs text-[#839E88] italic">
                                        {t('needsAdvisory')}
                                      </span>
                                      <button
                                        onClick={() => openAdvisoryEditor(item)}
                                        className="bg-[#1A3626] text-white px-3.5 py-1.5 rounded-lg text-xs font-bold hover:-translate-y-0.5 hover:shadow-md transition-all flex items-center gap-1.5"
                                      >
                                        <MessageSquare className="w-3.5 h-3.5" />
                                        {t('addAdvisory')}
                                      </button>
                                    </div>
                                  ) : (
                                    <div className="bg-[#F5F5F0] rounded-xl p-3.5 border border-[#1A3626]/15 space-y-2.5">
                                      <div className="flex items-center justify-between">
                                        <span className="text-xs uppercase tracking-wider font-extrabold text-[#1A3626]">
                                          {t('expertAdvisory')}
                                        </span>
                                        <button
                                          onClick={() => setEditingAdvisoryId(null)}
                                          className="text-xs text-[#839E88] hover:text-[#1A3626]"
                                        >
                                          {t('cancel')}
                                        </button>
                                      </div>
                                      <textarea
                                        rows={2}
                                        value={advisoryText}
                                        onChange={(e) => setAdvisoryText(e.target.value)}
                                        placeholder={t('writeAdvisoryPlaceholder')}
                                        className="w-full bg-white border border-[#1A3626]/20 rounded-lg p-2.5 text-sm text-[#1A3626] focus:ring-2 focus:ring-[#1A3626] outline-none resize-none"
                                      />
                                      <div className="flex justify-end gap-2">
                                        <button
                                          onClick={() => setEditingAdvisoryId(null)}
                                          className="px-3 py-1.5 text-xs text-[#57695D] hover:text-[#1A3626]"
                                        >
                                          {t('cancel')}
                                        </button>
                                        <button
                                          onClick={() => handleSaveAdvisory(item.id)}
                                          disabled={savingAdvisory || !advisoryText.trim()}
                                          className="bg-[#1A3626] text-white px-4 py-1.5 rounded-lg text-xs font-bold hover:shadow-md transition-all disabled:opacity-50 flex items-center gap-1.5"
                                        >
                                          {savingAdvisory ? (
                                            <div className="animate-spin rounded-full h-3 w-3 border-t-2 border-white"></div>
                                          ) : (
                                            <Send className="w-3 h-3" />
                                          )}
                                          {t('saveAdvisory')}
                                        </button>
                                      </div>
                                    </div>
                                  )}
                                </div>

                                {/* Toggle details accordion */}
                                <div className="mt-3 flex justify-end">
                                  <button
                                    onClick={() => setExpandedScanId(isExpanded ? null : item.id)}
                                    className="text-xs font-bold text-[#839E88] hover:text-[#1A3626] flex items-center gap-1"
                                  >
                                    <span>{isExpanded ? t('hidePractices') : t('allPractices')}</span>
                                    <ChevronDown
                                      className={`w-3.5 h-3.5 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                                    />
                                  </button>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Expandable Accordion with all Agricultural Practices */}
                          <AnimatePresence>
                            {isExpanded && (
                              <motion.div
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                                className="border-t border-[#1A3626]/10 bg-[#F5F5F0]/60 p-5 space-y-4"
                              >
                                {item.treatment && (
                                  <div className="bg-[#D7E8D6] border border-[#A3C4A5] rounded-xl p-3.5">
                                    <div className="flex items-center gap-2 mb-1">
                                      <Pill className="w-4 h-4 text-[#1A3626]" />
                                      <h4 className="text-xs uppercase tracking-wider font-extrabold text-[#1A3626]">
                                        {t('treatment')}
                                      </h4>
                                    </div>
                                    <p className="text-sm text-[#1A3626] leading-relaxed font-medium">
                                      {item.treatment}
                                    </p>
                                  </div>
                                )}

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                                  {[
                                    { items: item.cultural_practices, icon: Sprout, label: t('cultural') },
                                    { items: item.mechanical_practices, icon: Wrench, label: t('mechanical') },
                                    { items: item.biological_practices, icon: Bug, label: t('biological') },
                                    { items: item.chemical_practices, icon: FlaskConical, label: t('chemical') },
                                    { items: item.spray_timing, icon: Clock, label: t('sprayTiming') },
                                  ]
                                    .filter((s) => s.items && s.items.length > 0)
                                    .map((section, idx) => (
                                      <div
                                        key={idx}
                                        className="bg-white rounded-xl p-3 border border-[#1A3626]/10 shadow-2xs"
                                      >
                                        <div className="flex items-center gap-1.5 font-bold text-[#1A3626] mb-1.5">
                                          <section.icon className="w-3.5 h-3.5" />
                                          <span>{section.label}</span>
                                        </div>
                                        <ul className="pl-4 space-y-1">
                                          {section.items.map((p, pIdx) => (
                                            <li key={pIdx} className="text-[#57695D] list-disc leading-relaxed">
                                              {p}
                                            </li>
                                          ))}
                                        </ul>
                                      </div>
                                    ))}
                                </div>
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {/* 2. REGISTERED FARMERS TAB */}
            {activeTab === 'farmers' && (
              <div className="space-y-4">
                <div className="bg-[#FDFDFB] border border-[#1A3626]/10 rounded-2xl overflow-hidden shadow-[4px_4px_10px_rgba(26,54,38,0.03)]">
                  <div className="p-5 border-b border-[#1A3626]/10 flex items-center justify-between">
                    <div>
                      <h2 className="text-lg font-extrabold text-[#1A3626]">{t('registeredFarmers')}</h2>
                      <p className="text-xs text-[#839E88] mt-0.5">
                        {users.length} {t('registeredFarmers').toLowerCase()}
                      </p>
                    </div>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead className="bg-[#F5F5F0] text-[11px] uppercase tracking-wider font-extrabold text-[#839E88] border-b border-[#1A3626]/10">
                        <tr>
                          <th className="px-6 py-3.5">{t('farmer')}</th>
                          <th className="px-6 py-3.5">{t('name')}</th>
                          <th className="px-6 py-3.5">{t('mobile')}</th>
                          <th className="px-6 py-3.5">{t('joined')}</th>
                          <th className="px-6 py-3.5 text-center">{t('totalScans')}</th>
                          <th className="px-6 py-3.5 text-right">{t('actions')}</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-[#1A3626]/5 text-sm">
                        {users.map((u, i) => (
                          <tr key={i} className="hover:bg-[#F5F5F0]/50 transition-colors">
                            <td className="px-6 py-4 font-bold text-[#1A3626]">
                              <div className="flex items-center gap-2">
                                <div className="w-8 h-8 rounded-full bg-[#1A3626] text-white flex items-center justify-center text-xs font-bold uppercase">
                                  {u.username.slice(0, 2)}
                                </div>
                                <div>
                                  <p className="text-sm font-bold text-[#1A3626]">{u.username}</p>
                                  {u.role === 'admin' && (
                                    <span className="text-[10px] font-bold text-[#B36B00] bg-[#FCE5CD] px-1.5 py-0.2 rounded">
                                      Admin
                                    </span>
                                  )}
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4 text-[#57695D] font-medium">{u.name || '-'}</td>
                            <td className="px-6 py-4 text-[#57695D]">{u.mobile || '-'}</td>
                            <td className="px-6 py-4 text-xs text-[#839E88]">
                              {u.created_at ? format(new Date(u.created_at), 'PP') : '-'}
                            </td>
                            <td className="px-6 py-4 text-center">
                              <span className="px-3 py-1 bg-[#D7E8D6] text-[#1A3626] font-extrabold rounded-full text-xs">
                                {u.total_scans !== undefined ? u.total_scans : 0}
                              </span>
                            </td>
                            <td className="px-6 py-4 text-right">
                              <button
                                onClick={() => handleViewFarmerScans(u.username)}
                                className="inline-flex items-center gap-1.5 bg-[#1A3626] text-white px-3.5 py-1.5 rounded-lg text-xs font-bold hover:-translate-y-0.5 hover:shadow-md transition-all"
                              >
                                <span>{t('viewScans')}</span>
                                <ArrowRight className="w-3.5 h-3.5" />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* 3. OVERVIEW TAB */}
            {activeTab === 'overview' && (
              <div className="bg-[#FDFDFB] border border-[#1A3626]/10 rounded-2xl p-6 shadow-xs">
                <h2 className="text-xl font-extrabold text-[#1A3626] mb-4">{t('diseaseDistribution')}</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {stats?.disease_distribution?.map((item, idx) => (
                    <div
                      key={idx}
                      className="p-4 bg-[#F5F5F0] rounded-xl border border-[#1A3626]/10 flex items-center justify-between"
                    >
                      <span className="font-bold text-[#1A3626]">{item._id}</span>
                      <span className="text-2xl font-extrabold text-[#1A3626]">{item.count}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </motion.div>
    </Layout>
  );
};
