import React, { useState, useEffect } from 'react';
import { Layout } from '../components/Layout';
import { useTranslation } from 'react-i18next';
import { Users, ScanLine, PieChart, Clock, Download, CheckCircle2, XCircle, Pencil, History, ChevronDown, Bug, ShieldCheck, Pill, ShieldAlert, MessageSquare, Sprout, Wrench, FlaskConical } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { format } from 'date-fns';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const DISEASE_LIST = [
  "Brown Rust", "Mosaic", "Red Rot", "Healthy", "Unrecognized",
  "Brown Spot", "Early Shoot Borer", "Eye Spot", "Grassy Shoot Disease",
  "Internode Borer", "Leaf Footed Bug", "Mites", "Pokkah Boeng", "Pyrilla",
  "Scale Insect", "Whiplash Smut", "Wilt", "Woolly Aphids", "Top Shoot Borer",
  "White Grub", "Mealy Bug", "Grasshopper", "Yellow Leaf Disease", "Orange Rust", "Leafscald"
];

export const AdminPage = () => {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [detections, setDetections] = useState([]);
  const [pending, setPending] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('pending');
  const [downloading, setDownloading] = useState(false);
  const [reviewingId, setReviewingId] = useState(null);
  const [reviewForm, setReviewForm] = useState({ disease: '', severity: '', suggestion: '' });
  const [submitting, setSubmitting] = useState(null);
  const [expandedReviewId, setExpandedReviewId] = useState(null);
  const { t } = useTranslation();

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      const [statsRes, usersRes, detectionsRes, pendingRes] = await Promise.all([
        axios.get(`${API_URL}/api/admin/stats`, { withCredentials: true }),
        axios.get(`${API_URL}/api/admin/users`, { withCredentials: true }),
        axios.get(`${API_URL}/api/admin/detections`, { withCredentials: true }),
        axios.get(`${API_URL}/api/admin/pending`, { withCredentials: true })
      ]);
      setStats(statsRes.data); setUsers(usersRes.data); setDetections(detectionsRes.data); setPending(pendingRes.data);
    } catch (error) { console.error('Failed:', error); }
    finally { setLoading(false); }
  };

  const handleReview = async (id, action) => {
    setSubmitting(id + action);
    try {
      const body = { action, suggestion: reviewForm.suggestion || '' };
      if (action === 'approve') { body.disease = reviewForm.disease || undefined; body.severity = reviewForm.severity || undefined; }
      await axios.post(`${API_URL}/api/admin/review/${id}`, body, { withCredentials: true });
      setReviewingId(null); setReviewForm({ disease: '', severity: '', suggestion: '' });
      await fetchData();
    } catch (e) { alert('Review failed.'); }
    finally { setSubmitting(null); }
  };

  const openReview = (item) => { setReviewingId(item.id); setReviewForm({ disease: item.ai_disease || item.disease, severity: item.ai_severity || item.severity, suggestion: '' }); };

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const res = await axios.get(`${API_URL}/api/admin/download-images`, { withCredentials: true, responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement('a'); a.href = url; a.setAttribute('download', `images_${new Date().toISOString().slice(0,10)}.zip`);
      document.body.appendChild(a); a.click(); a.remove(); window.URL.revokeObjectURL(url);
    } catch (e) { alert(e.response?.status === 404 ? 'No images yet.' : 'Download failed.'); }
    finally { setDownloading(false); }
  };

  const severityColor = (s) => ({ high: 'bg-[#F5D0C9] text-[#8F2C1A]', medium: 'bg-[#FCE5CD] text-[#B36B00]', low: 'bg-[#D7E8D6] text-[#1A3626]' }[s] || 'bg-[#E8E8E3] text-[#57695D]');
  const statusBadge = (s) => ({ approved: <span className="px-2 py-1 rounded-full text-xs font-bold bg-[#D7E8D6] text-[#1A3626]">Approved</span>, rejected: <span className="px-2 py-1 rounded-full text-xs font-bold bg-[#F5D0C9] text-[#8F2C1A]">Rejected</span> }[s] || <span className="px-2 py-1 rounded-full text-xs font-bold bg-[#FCE5CD] text-[#B36B00]">Pending</span>);
  const reviewed = detections.filter(d => d.status === 'approved' || d.status === 'rejected');

  const tabs = [
    { id: 'pending', label: `Pending (${pending.length})` },
    { id: 'reviewed', label: `Reviewed (${reviewed.length})` },
    { id: 'overview', label: 'Overview' },
    { id: 'users', label: 'Users' },
    { id: 'scans', label: 'All Scans' },
  ];

  return (
    <Layout>
      <motion.div data-testid="admin-page" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
          <div>
            <h1 className="text-4xl sm:text-5xl font-extrabold text-[#1A3626] tracking-tight mb-1">{t('admin')}</h1>
            <p className="text-base text-[#57695D]">Manage users, review scans, and view analytics</p>
          </div>
          <button data-testid="admin-download-zip-button" onClick={handleDownload} disabled={downloading}
            className="mt-4 sm:mt-0 bg-[#1A3626] text-[#FDFDFB] px-5 py-2.5 rounded-lg font-semibold flex items-center space-x-2 transition-all hover:-translate-y-0.5 hover:shadow-lg hover:shadow-[#1A3626]/20 disabled:opacity-50 text-sm">
            {downloading ? <><div className="animate-spin rounded-full h-4 w-4 border-t-2 border-white"></div><span>Preparing...</span></> : <><Download className="w-4 h-4" /><span>Download Images (ZIP)</span></>}
          </button>
        </div>

        {loading ? (
          <div className="text-center py-16"><div className="animate-spin rounded-full h-10 w-10 border-t-3 border-[#1A3626] mx-auto"></div></div>
        ) : (
          <>
            {/* Stats Grid */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              {[
                { label: t('totalUsers'), value: stats?.total_users || 0, icon: Users, color: '#1A3626' },
                { label: t('totalScans'), value: stats?.total_scans || 0, icon: ScanLine, color: '#1A3626' },
                { label: 'Pending', value: pending.length, icon: Clock, color: '#B36B00' },
                { label: 'Diseases', value: stats?.disease_distribution?.length || 0, icon: PieChart, color: '#1A3626' },
              ].map((s, i) => (
                <div key={i} className="bg-[#FDFDFB] border border-[#1A3626]/10 rounded-xl p-5 shadow-[4px_4px_10px_rgba(26,54,38,0.05),-4px_-4px_10px_rgba(255,255,255,1)]">
                  <div className="flex items-center justify-between">
                    <div><p className="text-xs uppercase tracking-[0.2em] font-semibold" style={{ color: s.color === '#B36B00' ? '#B36B00' : '#839E88' }}>{s.label}</p><p className="text-3xl font-extrabold text-[#1A3626] mt-1">{s.value}</p></div>
                    <div className="w-11 h-11 rounded-xl flex items-center justify-center" style={{ backgroundColor: s.color === '#B36B00' ? '#FCE5CD' : '#E8E8E3' }}>
                      <s.icon className="w-5 h-5" style={{ color: s.color }} />
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Tabs */}
            <div className="flex space-x-1 mb-8 overflow-x-auto border-b border-[#1A3626]/10 pb-px">
              {tabs.map(tab => (
                <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                  className={`pb-3 px-4 text-sm font-semibold whitespace-nowrap transition-all ${activeTab === tab.id ? 'text-[#1A3626] border-b-2 border-[#1A3626]' : 'text-[#839E88] hover:text-[#57695D]'}`}>
                  {tab.label}
                </button>
              ))}
            </div>

            {/* PENDING */}
            {activeTab === 'pending' && (
              <div className="space-y-4">
                {pending.length === 0 ? (
                  <div className="bg-[#FDFDFB] border border-[#1A3626]/10 rounded-2xl p-16 text-center">
                    <CheckCircle2 className="w-16 h-16 mx-auto text-[#1A3626] mb-4" strokeWidth={1} />
                    <p className="text-lg font-semibold text-[#1A3626]">All caught up!</p>
                    <p className="text-[#839E88] mt-1">No pending scans to review.</p>
                  </div>
                ) : pending.map(item => (
                  <div key={item.id} data-testid={`pending-item-${item.id}`} className="bg-[#FDFDFB] border border-[#1A3626]/10 rounded-xl overflow-hidden">
                    <div className="p-6">
                      <div className="flex gap-5">
                        <div className="w-36 h-36 rounded-xl overflow-hidden flex-shrink-0 bg-[#E8E8E3]">
                          <img src={`${API_URL}/api/files/${item.image_path}`} alt="" className="w-full h-full object-cover" />
                        </div>
                        {item.overlay_path && (
                          <div className="w-36 h-36 rounded-xl overflow-hidden flex-shrink-0 bg-[#E8E8E3] relative">
                            <img src={`${API_URL}/api/files/${item.overlay_path}`} alt="AI Segmentation" className="w-full h-full object-cover" />
                          </div>
                        )}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between mb-3">
                            <div>
                              <p className="text-sm text-[#839E88]">By <span className="font-bold text-[#1A3626]">{item.username}</span></p>
                              <p className="text-xs text-[#839E88]">{format(new Date(item.created_at), 'PPpp')}</p>
                            </div>
                            <span className="px-3 py-1 rounded-full text-xs font-bold bg-[#FCE5CD] text-[#B36B00] border border-[#F3C185]">Pending</span>
                          </div>

                          <div className="bg-[#F5F5F0] rounded-lg p-3 mb-3">
                            <p className="text-xs uppercase tracking-[0.2em] font-bold text-[#839E88] mb-1">AI Prediction</p>
                            <div className="flex items-center gap-2">
                              <span className="text-base font-bold text-[#1A3626]">{item.ai_disease || item.disease}</span>
                              <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${severityColor(item.ai_severity || item.severity)}`}>{item.ai_severity || item.severity}</span>
                            </div>
                          </div>

                          {/* All Practices */}
                          <div className="bg-[#D7E8D6] border border-[#A3C4A5] rounded-lg p-3 mb-3 space-y-2">
                            <p className="text-xs uppercase tracking-[0.2em] font-bold text-[#1A3626]">Practices</p>
                            {item.treatment && <p className="text-sm text-[#57695D]"><Pill className="w-3.5 h-3.5 inline mr-1 text-[#1A3626]" /><span className="font-medium text-[#1A3626]">Treatment:</span> {item.treatment}</p>}
                            {[
                              { items: item.cultural_practices, icon: Sprout, label: 'Cultural' },
                              { items: item.mechanical_practices, icon: Wrench, label: 'Mechanical' },
                              { items: item.biological_practices, icon: Bug, label: 'Biological' },
                              { items: item.chemical_practices, icon: FlaskConical, label: 'Chemical' },
                              { items: item.spray_timing, icon: Clock, label: 'Spray Timing' },
                            ].filter(s => s.items?.length > 0).map((section, si) => (
                              <div key={si}>
                                <span className="text-xs font-bold text-[#839E88]"><section.icon className="w-3 h-3 inline mr-1" />{section.label}:</span>
                                <ul className="pl-4 mt-0.5">{section.items.map((p,i) => <li key={i} className="text-xs text-[#57695D] list-disc">{p}</li>)}</ul>
                              </div>
                            ))}
                          </div>

                          {reviewingId !== item.id ? (
                            <div className="flex gap-2">
                              <button data-testid={`review-btn-${item.id}`} onClick={() => openReview(item)}
                                className="flex items-center gap-1.5 bg-[#1A3626] text-[#FDFDFB] px-4 py-2 rounded-lg font-medium text-sm hover:-translate-y-0.5 hover:shadow-md transition-all">
                                <Pencil className="w-3.5 h-3.5" /> Review
                              </button>
                              <button onClick={() => openReview(item)}
                                className="flex items-center gap-1.5 bg-[#FDFDFB] border-2 border-[#C25E4B] text-[#C25E4B] hover:bg-[#F5D0C9] px-4 py-2 rounded-lg font-medium text-sm transition-all">
                                <XCircle className="w-3.5 h-3.5" /> Reject
                              </button>
                            </div>
                          ) : (
                            <div className="border-t border-[#1A3626]/10 pt-4 mt-3 space-y-3">
                              <div className="grid grid-cols-2 gap-3">
                                <div>
                                  <label className="text-xs uppercase tracking-[0.2em] text-[#839E88] font-bold block mb-1">Disease</label>
                                  <select data-testid="review-disease-select" value={reviewForm.disease} onChange={e => setReviewForm({...reviewForm, disease: e.target.value})}
                                    className="w-full bg-[#FDFDFB] border border-[#839E88]/40 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[#1A3626] outline-none">
                                    {DISEASE_LIST.map(d => <option key={d} value={d}>{d}</option>)}
                                  </select>
                                </div>
                                <div>
                                  <label className="text-xs uppercase tracking-[0.2em] text-[#839E88] font-bold block mb-1">Severity</label>
                                  <select data-testid="review-severity-select" value={reviewForm.severity} onChange={e => setReviewForm({...reviewForm, severity: e.target.value})}
                                    className="w-full bg-[#FDFDFB] border border-[#839E88]/40 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[#1A3626] outline-none">
                                    <option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option>
                                  </select>
                                </div>
                              </div>
                              <div>
                                <label className="text-xs uppercase tracking-[0.2em] text-[#839E88] font-bold block mb-1">Suggestion for Farmer</label>
                                <textarea data-testid="review-suggestion-input" value={reviewForm.suggestion} onChange={e => setReviewForm({...reviewForm, suggestion: e.target.value})}
                                  placeholder="Add your suggestion..." rows={3}
                                  className="w-full bg-[#FDFDFB] border border-[#839E88]/40 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-[#1A3626] outline-none resize-none" />
                              </div>
                              <div className="flex gap-2">
                                <button data-testid={`admin-approve-button`} onClick={() => handleReview(item.id, 'approve')} disabled={!!submitting}
                                  className="flex items-center gap-1.5 bg-[#1A3626] text-white px-5 py-2 rounded-lg font-medium text-sm disabled:opacity-50 hover:shadow-md transition-all">
                                  {submitting === item.id+'approve' ? <div className="animate-spin h-4 w-4 border-t-2 border-white rounded-full"></div> : <CheckCircle2 className="w-4 h-4" />} Approve
                                </button>
                                <button data-testid={`admin-reject-button`} onClick={() => handleReview(item.id, 'reject')} disabled={!!submitting}
                                  className="flex items-center gap-1.5 bg-[#C25E4B] text-white px-5 py-2 rounded-lg font-medium text-sm disabled:opacity-50 hover:bg-[#A34B3A] transition-all">
                                  {submitting === item.id+'reject' ? <div className="animate-spin h-4 w-4 border-t-2 border-white rounded-full"></div> : <XCircle className="w-4 h-4" />} Reject
                                </button>
                                <button onClick={() => { setReviewingId(null); setReviewForm({ disease: '', severity: '', suggestion: '' }); }}
                                  className="text-[#839E88] hover:text-[#1A3626] px-4 py-2 text-sm transition-colors">Cancel</button>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* REVIEWED */}
            {activeTab === 'reviewed' && (
              <div className="space-y-4">
                {reviewed.length === 0 ? (
                  <div className="bg-[#FDFDFB] border border-[#1A3626]/10 rounded-2xl p-16 text-center">
                    <History className="w-16 h-16 mx-auto text-[#E8E8E3] mb-4" strokeWidth={1} />
                    <p className="text-lg font-semibold text-[#1A3626]">No reviewed scans yet</p>
                  </div>
                ) : reviewed.map(item => (
                  <div key={item.id} className="bg-[#FDFDFB] border border-[#1A3626]/10 rounded-xl overflow-hidden">
                    <div className="p-5 cursor-pointer hover:bg-[#F5F5F0]/50 transition-colors" onClick={() => setExpandedReviewId(expandedReviewId === item.id ? null : item.id)}>
                      <div className="flex gap-5">
                        <div className="w-28 h-28 rounded-xl overflow-hidden flex-shrink-0 bg-[#E8E8E3]">
                          <img src={`${API_URL}/api/files/${item.image_path}`} alt="" className="w-full h-full object-cover" />
                        </div>
                        {item.overlay_path && (
                          <div className="w-28 h-28 rounded-xl overflow-hidden flex-shrink-0 bg-[#E8E8E3] relative">
                            <img src={`${API_URL}/api/files/${item.overlay_path}`} alt="AI Segmentation" className="w-full h-full object-cover" />
                          </div>
                        )}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between mb-2">
                            <div>
                              <p className="text-sm text-[#839E88]">Farmer: <span className="font-bold text-[#1A3626]">{item.username}</span></p>
                              <p className="text-xs text-[#839E88]">{format(new Date(item.created_at), 'PPpp')}</p>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className={`px-3 py-1 rounded-full text-xs font-bold border ${item.status === 'approved' ? 'bg-[#D7E8D6] text-[#1A3626] border-[#A3C4A5]' : 'bg-[#F5D0C9] text-[#8F2C1A] border-[#E29D90]'}`}>
                                {item.status === 'approved' ? 'Approved' : 'Rejected'}
                              </span>
                              <ChevronDown className={`w-4 h-4 text-[#839E88] transition-transform ${expandedReviewId === item.id ? 'rotate-180' : ''}`} />
                            </div>
                          </div>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-base font-bold text-[#1A3626]">{item.disease}</span>
                            <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${severityColor(item.severity)}`}>{item.severity}</span>
                          </div>
                          {item.ai_disease && item.ai_disease !== item.disease && (
                            <p className="text-xs text-[#839E88]">AI: <span className="line-through">{item.ai_disease}</span> → <span className="font-semibold text-[#1A3626]">{item.disease}</span></p>
                          )}
                          {item.admin_suggestion && <p className="text-xs text-[#57695D] mt-1 line-clamp-1">Suggestion: {item.admin_suggestion}</p>}
                        </div>
                      </div>
                    </div>
                    <AnimatePresence>
                      {expandedReviewId === item.id && item.status === 'approved' && (
                        <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}
                          className="border-t border-[#1A3626]/10 bg-[#F5F5F0] overflow-hidden">
                          <div className="p-6 space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <div><div className="flex items-center gap-2 mb-1"><Bug className="w-4 h-4 text-[#C25E4B]" /><h4 className="text-xs uppercase tracking-[0.2em] font-bold text-[#839E88]">Symptoms</h4></div><p className="text-sm text-[#57695D]">{item.symptoms}</p></div>
                              <div><div className="flex items-center gap-2 mb-1"><ShieldAlert className="w-4 h-4 text-[#B36B00]" /><h4 className="text-xs uppercase tracking-[0.2em] font-bold text-[#839E88]">Causes</h4></div><p className="text-sm text-[#57695D]">{item.causes}</p></div>
                              <div><div className="flex items-center gap-2 mb-1"><Pill className="w-4 h-4 text-[#1A3626]" /><h4 className="text-xs uppercase tracking-[0.2em] font-bold text-[#839E88]">Treatment</h4></div><p className="text-sm text-[#57695D]">{item.treatment}</p></div>
                              <div><div className="flex items-center gap-2 mb-1"><ShieldCheck className="w-4 h-4 text-[#839E88]" /><h4 className="text-xs uppercase tracking-[0.2em] font-bold text-[#839E88]">Prevention</h4></div><p className="text-sm text-[#57695D]">{item.prevention}</p></div>
                            </div>
                            {item.admin_suggestion && (
                              <div className="bg-[#FDFDFB] border-l-4 border-[#1A3626] rounded-r-xl p-4">
                                <div className="flex items-center gap-2 mb-1"><MessageSquare className="w-4 h-4 text-[#1A3626]" /><h4 className="text-xs uppercase tracking-[0.2em] font-bold text-[#839E88]">Your Suggestion</h4></div>
                                <p className="text-sm text-[#57695D]">{item.admin_suggestion}</p>
                              </div>
                            )}
                            {item.reviewed_at && <p className="text-xs text-[#839E88]">Reviewed: {format(new Date(item.reviewed_at), 'PPpp')}</p>}
                          </div>
                        </motion.div>
                      )}
                      {expandedReviewId === item.id && item.status === 'rejected' && (
                        <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}
                          className="border-t border-[#E29D90] bg-[#F5D0C9]/20 overflow-hidden">
                          <div className="p-5">
                            <p className="text-sm text-[#8F2C1A] font-medium">Rejected</p>
                            {item.admin_suggestion && <p className="text-sm text-[#57695D] mt-1">{item.admin_suggestion}</p>}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                ))}
              </div>
            )}

            {/* OVERVIEW */}
            {activeTab === 'overview' && (
              <div className="bg-[#FDFDFB] border border-[#1A3626]/10 rounded-xl p-6">
                <h2 className="text-xl font-bold text-[#1A3626] mb-4">{t('diseaseDistribution')}</h2>
                <div className="space-y-2">
                  {stats?.disease_distribution?.map((item, idx) => (
                    <div key={idx} className="flex items-center justify-between p-4 bg-[#F5F5F0] rounded-lg hover:bg-[#E8E8E3] transition-colors">
                      <span className="font-medium text-[#1A3626]">{item._id}</span>
                      <span className="text-2xl font-extrabold text-[#1A3626]">{item.count}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* USERS */}
            {activeTab === 'users' && (
              <div className="bg-[#FDFDFB] border border-[#1A3626]/10 rounded-xl overflow-hidden">
                <table className="w-full">
                  <thead className="bg-[#E8E8E3]">
                    <tr>{['Username','Name','Mobile','Role','Joined'].map(h => <th key={h} className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] font-bold text-[#839E88]">{h}</th>)}</tr>
                  </thead>
                  <tbody className="divide-y divide-[#1A3626]/5">
                    {users.map((u, i) => (
                      <tr key={i} className="hover:bg-[#F5F5F0] transition-colors">
                        <td className="px-6 py-4 text-sm font-medium text-[#1A3626]">{u.username}</td>
                        <td className="px-6 py-4 text-sm text-[#57695D]">{u.name || '-'}</td>
                        <td className="px-6 py-4 text-sm text-[#57695D]">{u.mobile || '-'}</td>
                        <td className="px-6 py-4"><span className={`px-2 py-1 rounded-full text-xs font-bold ${u.role === 'admin' ? 'bg-[#1A3626] text-white' : 'bg-[#E8E8E3] text-[#1A3626]'}`}>{u.role}</span></td>
                        <td className="px-6 py-4 text-sm text-[#839E88]">{format(new Date(u.created_at), 'PP')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* ALL SCANS */}
            {activeTab === 'scans' && (
              <div className="bg-[#FDFDFB] border border-[#1A3626]/10 rounded-xl overflow-hidden">
                <table className="w-full">
                  <thead className="bg-[#E8E8E3]">
                    <tr>{['User','Disease','Severity','Status','Date'].map(h => <th key={h} className="px-6 py-4 text-left text-xs uppercase tracking-[0.2em] font-bold text-[#839E88]">{h}</th>)}</tr>
                  </thead>
                  <tbody className="divide-y divide-[#1A3626]/5">
                    {detections.slice(0, 30).map((d, i) => (
                      <tr key={i} className="hover:bg-[#F5F5F0] transition-colors">
                        <td className="px-6 py-4 text-sm text-[#1A3626]">{d.username}</td>
                        <td className="px-6 py-4 text-sm font-medium text-[#1A3626]">{d.disease}</td>
                        <td className="px-6 py-4"><span className={`px-2 py-1 rounded-full text-xs font-bold ${severityColor(d.severity)}`}>{d.severity}</span></td>
                        <td className="px-6 py-4">{statusBadge(d.status)}</td>
                        <td className="px-6 py-4 text-sm text-[#839E88]">{format(new Date(d.created_at), 'PP p')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </motion.div>
    </Layout>
  );
};
