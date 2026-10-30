import React, { useState, useRef } from 'react';
import { Layout } from '../components/Layout';
import { useTranslation } from 'react-i18next';
import { Upload, ScanLine, Clock, SendHorizonal, RotateCcw, AlertTriangle, Sprout, Wrench, Bug, FlaskConical, ChevronDown, Leaf, Pill, ShieldAlert, ShieldCheck } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const PracticeAccordion = ({ section }) => {
  const [open, setOpen] = useState(false);
  const Icon = section.icon;
  return (
    <div className="border border-[#1A3626]/10 rounded-lg overflow-hidden">
      <button onClick={() => setOpen(!open)} className="w-full flex items-center justify-between p-3 hover:bg-[#F5F5F0] transition-colors">
        <div className="flex items-center gap-2">
          <div className={`w-7 h-7 rounded-lg ${section.color} flex items-center justify-center`}><Icon className="w-3.5 h-3.5 text-white" /></div>
          <span className="font-semibold text-[#1A3626] text-xs">{section.label}</span>
          <span className="text-[10px] text-[#839E88] bg-[#E8E8E3] px-1.5 py-0.5 rounded-full">{section.items.length}</span>
        </div>
        <ChevronDown className={`w-3.5 h-3.5 text-[#839E88] transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && (
        <div className="px-3 pb-3 space-y-1">
          {section.items.map((item, i) => (
            <div key={i} className="flex items-start gap-2 text-xs text-[#57695D] bg-[#F5F5F0] rounded-md px-3 py-2">
              <span className="w-1.5 h-1.5 rounded-full bg-[#839E88] mt-1 flex-shrink-0" />
              <span className="leading-relaxed">{item}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const severityBadge = (sev) => {
  const s = (sev || 'low').toLowerCase();
  if (s === 'high') return 'bg-[#F5D0C9] text-[#8F2C1A] border-[#E29D90]';
  if (s === 'medium') return 'bg-[#FCE5CD] text-[#B36B00] border-[#F3C185]';
  return 'bg-[#D7E8D6] text-[#1A3626] border-[#A3C4A5]';
};

export const DashboardPage = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [detecting, setDetecting] = useState(false);
  const [result, setResult] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);
  const { t, i18n } = useTranslation();

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file);
      setResult(null);
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result);
      reader.readAsDataURL(file);
    }
  };

  const handleDrag = (e) => { e.preventDefault(); e.stopPropagation(); setDragActive(e.type === 'dragenter' || e.type === 'dragover'); };
  const handleDrop = (e) => {
    e.preventDefault(); setDragActive(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file); setResult(null);
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result);
      reader.readAsDataURL(file);
    }
  };

  const handleDetect = async () => {
    if (!selectedFile) return;
    setDetecting(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    try {
      const lang = i18n.language || 'en';
      const { data } = await axios.post(`${API_URL}/api/detect?lang=${lang}`, formData, { headers: { 'Content-Type': 'multipart/form-data' }, withCredentials: true });
      setResult(data);
    } catch (error) {
      alert(t('detectionFailed'));
    } finally {
      setDetecting(false);
    }
  };

  const handleNewScan = () => { setSelectedFile(null); setPreview(null); setResult(null); };

  return (
    <Layout>
      <motion.div data-testid="dashboard-page" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-4xl sm:text-5xl font-extrabold text-[#1A3626] tracking-tight mb-1">{t('dashboard')}</h1>
        <p className="text-base text-[#57695D] mb-10 leading-relaxed">{t('dashboardSubtitle')}</p>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          {/* Upload Area - Takes 3 cols */}
          <div className="lg:col-span-3 space-y-6">
            <div
              data-testid="upload-dropzone"
              onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}
              onClick={() => !result && fileInputRef.current?.click()}
              className={`relative border-2 border-dashed rounded-2xl min-h-[380px] flex items-center justify-center transition-all duration-300 overflow-hidden ${
                dragActive ? 'border-[#1A3626] bg-[#1A3626]/5 scale-[1.01]' :
                preview ? 'border-[#839E88]/30 bg-[#FDFDFB]' :
                'border-[#839E88] bg-[#E8E8E3]/50 hover:bg-[#E8E8E3] hover:border-[#1A3626] cursor-pointer'
              }`}
            >
              {preview ? (
                <img src={preview} alt="Preview" className="w-full h-full object-contain p-4" />
              ) : (
                <div className="text-center p-8">
                  <div className="w-20 h-20 mx-auto mb-5 bg-[#1A3626]/5 rounded-2xl flex items-center justify-center">
                    <Upload className="w-10 h-10 text-[#839E88]" strokeWidth={1.5} />
                  </div>
                  <p className="text-[#1A3626] font-semibold text-lg mb-1">{t('uploadImage')}</p>
                  <p className="text-sm text-[#839E88]">{t('dragDrop')}</p>
                  <p className="text-xs text-[#839E88]/70 mt-3">{t('fileHint')}</p>
                </div>
              )}
            </div>
            <input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileSelect} className="hidden" />

            {!result ? (
              <button
                data-testid="detect-disease-button"
                onClick={handleDetect}
                disabled={!selectedFile || detecting}
                className="w-full bg-[#1A3626] text-[#FDFDFB] py-4 rounded-xl font-semibold text-lg flex items-center justify-center space-x-3 transition-all hover:-translate-y-0.5 hover:shadow-xl hover:shadow-[#1A3626]/20 disabled:opacity-40 disabled:hover:translate-y-0 disabled:hover:shadow-none active:translate-y-0"
              >
                {detecting ? (
                  <><div className="animate-spin rounded-full h-6 w-6 border-t-2 border-[#FDFDFB]"></div><span>{t('analyzing')}</span></>
                ) : (
                  <><ScanLine className="w-6 h-6" /><span>{t('detectDisease')}</span></>
                )}
              </button>
            ) : (
              <button data-testid="new-scan-button" onClick={handleNewScan}
                className="w-full bg-[#E8E8E3] text-[#1A3626] py-4 rounded-xl font-semibold text-lg flex items-center justify-center space-x-3 transition-all hover:bg-[#839E88] hover:text-[#FDFDFB]">
                <RotateCcw className="w-5 h-5" /><span>{t('newScan')}</span>
              </button>
            )}
          </div>

          {/* Result Area - Takes 2 cols */}
          <div className="lg:col-span-2">
            <AnimatePresence mode="wait">
              {result ? (
                <motion.div key="result" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}
                  data-testid="detection-result"
                  className="bg-[#FDFDFB] border border-[#1A3626]/10 rounded-2xl shadow-[4px_4px_10px_rgba(26,54,38,0.05),-4px_-4px_10px_rgba(255,255,255,1)] p-7 space-y-5"
                >
                  {result.overlay_path && result.disease !== 'Unrecognized' && (
                    <div className="rounded-xl overflow-hidden bg-[#E8E8E3]">
                      <img src={`${API_URL}/api/files/${result.overlay_path}`} alt="Segmentation" className="w-full h-auto" />
                    </div>
                  )}

                  {/* Disease Header */}
                  <div className="bg-[#F5F5F0] rounded-xl p-4 border border-[#1A3626]/10 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs uppercase tracking-[0.2em] font-bold text-[#839E88]">{t('disease')}</span>
                      {result.disease === 'Unrecognized' ? (
                        <span className="px-2.5 py-0.5 rounded-full text-xs font-bold border uppercase tracking-wider bg-[#FCE5CD] text-[#B36B00] border-[#F3C185]">
                          {t('notSupported')}
                        </span>
                      ) : (
                        <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold border uppercase tracking-wider ${severityBadge(result.severity || result.ai_severity)}`}>
                          {result.severity || result.ai_severity}
                        </span>
                      )}
                    </div>
                    <div>
                      <h3 className="text-2xl font-extrabold text-[#1A3626]">
                        {result.disease === 'Unrecognized' ? t('unrecognizedDisease') : (result.disease_name_local || result.disease)}
                      </h3>
                      {result.disease !== 'Unrecognized' && result.disease_name_local && result.disease_name_local !== result.disease && (
                        <p className="text-xs text-[#839E88] font-medium mt-0.5">({result.disease})</p>
                      )}
                    </div>

                    {result.disease !== 'Unrecognized' && result.ai_predictions && result.ai_predictions.length > 1 && (
                      <div className="pt-2 border-t border-[#1A3626]/10 space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] uppercase tracking-wider font-bold text-[#839E88]">{t('aiDetectionModels')}</span>
                          {result.is_co_infection && (
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-[#FCE5CD] text-[#B36B00] border border-[#F3C185]">
                              {t('dualDetection')}
                            </span>
                          )}
                        </div>
                        <div className="space-y-1.5">
                          {result.ai_predictions.map((p, idx) => (
                            <div key={idx} className="bg-white rounded-lg p-2.5 border border-[#1A3626]/10 flex items-center justify-between shadow-xs">
                              <div className="flex items-center gap-2">
                                <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: p.disease === 'Red Rot' ? '#DC2626' : (p.disease === 'Brown Rust' ? '#EA580C' : '#84CC16') }}></span>
                                <p className="text-sm font-bold text-[#1A3626]">{p.disease}</p>
                              </div>
                              <div className="flex items-center gap-2">
                                <span className="text-xs font-semibold text-[#57695D]">{Math.round((p.confidence || 0) * 100)}%</span>
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold border uppercase tracking-wider ${severityBadge(p.severity)}`}>{p.severity}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {result.disease === 'Unrecognized' ? (
                    <div className="bg-[#FCE5CD]/60 border border-[#F3C185] rounded-xl p-5 space-y-3">
                      <div className="flex items-start space-x-3">
                        <AlertTriangle className="w-7 h-7 text-[#B36B00] flex-shrink-0 mt-0.5" />
                        <div>
                          <h3 className="text-base font-bold text-[#B36B00]">{t('unrecognizedDisease')}</h3>
                          <p className="text-sm text-[#57695D] mt-1.5 leading-relaxed">{t('unrecognizedMsg')}</p>
                        </div>
                      </div>
                      <div className="bg-white/80 rounded-lg p-3 border border-[#F3C185]/40 text-xs space-y-1.5">
                        <p className="font-bold text-[#1A3626]">🌿 Supported Sugarcane Leaf Diseases:</p>
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-1">
                          <div className="p-2 bg-[#F5F5F0] rounded border border-[#1A3626]/10 font-semibold text-[#1A3626]">1. Brown Rust</div>
                          <div className="p-2 bg-[#F5F5F0] rounded border border-[#1A3626]/10 font-semibold text-[#1A3626]">2. Red Rot</div>
                          <div className="p-2 bg-[#F5F5F0] rounded border border-[#1A3626]/10 font-semibold text-[#1A3626]">3. Mosaic</div>
                        </div>
                      </div>
                    </div>
                  ) : result.disease === 'Healthy' ? (
                    <div className="bg-[#D7E8D6] border border-[#A3C4A5] rounded-xl p-5">
                      <div className="flex items-start space-x-3">
                        <ShieldCheck className="w-7 h-7 text-[#1A3626] flex-shrink-0 mt-0.5" />
                        <div>
                          <h3 className="text-base font-bold text-[#1A3626]">{result.disease_name_local || t('healthy')}</h3>
                          <p className="text-sm text-[#57695D] mt-1.5 leading-relaxed">{result.symptoms || t('healthyTissueMsg')}</p>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <>
                      {/* Immediate Treatment Card */}
                      {result.treatment && (
                        <div className="bg-[#D7E8D6] border border-[#A3C4A5] rounded-xl p-4">
                          <div className="flex items-center gap-2 mb-1.5">
                            <Pill className="w-4 h-4 text-[#1A3626]" />
                            <h4 className="text-xs uppercase tracking-[0.2em] font-bold text-[#1A3626]">{t('treatment')}</h4>
                          </div>
                          <p className="text-sm text-[#1A3626] leading-relaxed font-medium">{result.treatment}</p>
                        </div>
                      )}

                      {/* Symptoms & Causes Grid */}
                      <div className="grid grid-cols-1 gap-3">
                        {result.symptoms && (
                          <div className="bg-[#F5F5F0] rounded-xl p-3.5 border border-[#1A3626]/10">
                            <div className="flex items-center gap-2 mb-1">
                              <Bug className="w-4 h-4 text-[#C25E4B]" />
                              <h4 className="text-xs uppercase tracking-[0.2em] font-bold text-[#839E88]">{t('symptoms')}</h4>
                            </div>
                            <p className="text-xs text-[#57695D] leading-relaxed whitespace-pre-line">{result.symptoms}</p>
                          </div>
                        )}
                        {result.causes && (
                          <div className="bg-[#F5F5F0] rounded-xl p-3.5 border border-[#1A3626]/10">
                            <div className="flex items-center gap-2 mb-1">
                              <ShieldAlert className="w-4 h-4 text-[#B36B00]" />
                              <h4 className="text-xs uppercase tracking-[0.2em] font-bold text-[#839E88]">{t('causes')}</h4>
                            </div>
                            <p className="text-xs text-[#57695D] leading-relaxed">{result.causes}</p>
                          </div>
                        )}
                        {result.prevention && (
                          <div className="bg-[#F5F5F0] rounded-xl p-3.5 border border-[#1A3626]/10">
                            <div className="flex items-center gap-2 mb-1">
                              <ShieldCheck className="w-4 h-4 text-[#1A3626]" />
                              <h4 className="text-xs uppercase tracking-[0.2em] font-bold text-[#839E88]">{t('prevention')}</h4>
                            </div>
                            <p className="text-xs text-[#57695D] leading-relaxed">{result.prevention}</p>
                          </div>
                        )}
                      </div>

                      {/* Management Practices Accordions */}
                      {(result.cultural_practices?.length > 0 || result.mechanical_practices?.length > 0 || result.biological_practices?.length > 0 || result.chemical_practices?.length > 0 || result.spray_timing?.length > 0) && (
                        <div className="space-y-2 pt-1">
                          <p className="text-xs uppercase tracking-[0.2em] font-bold text-[#839E88]">
                            {t('managementPractices')}
                          </p>
                          {[
                            { items: result.cultural_practices || [], icon: Sprout, label: t('culturalPractices'), color: 'bg-[#1A3626]' },
                            { items: result.mechanical_practices || [], icon: Wrench, label: t('mechanicalPractices'), color: 'bg-[#57695D]' },
                            { items: result.biological_practices || [], icon: Bug, label: t('biologicalPractices'), color: 'bg-[#839E88]' },
                            { items: result.chemical_practices || [], icon: FlaskConical, label: t('chemicalPractices'), color: 'bg-[#C25E4B]' },
                            { items: result.spray_timing || [], icon: Clock, label: t('sprayTiming'), color: 'bg-[#B36B00]' },
                          ].filter(s => s.items.length > 0).map((section, idx) => (
                            <PracticeAccordion key={idx} section={section} />
                          ))}
                        </div>
                      )}

                      {/* Chemical Reference Table */}
                      {result.chemical_reference?.length > 0 && (
                        <div className="bg-[#F5F5F0] border border-[#1A3626]/10 rounded-xl p-3.5 space-y-2">
                          <div className="flex items-center gap-1.5">
                            <FlaskConical className="w-3.5 h-3.5 text-[#C25E4B]" />
                            <h4 className="text-xs uppercase tracking-[0.2em] font-bold text-[#1A3626]">
                              {t('chemicalReference')}
                            </h4>
                          </div>
                          <div className="overflow-x-auto">
                            <table className="w-full text-xs">
                              <thead>
                                <tr className="text-left text-[#839E88] uppercase tracking-wider border-b border-[#1A3626]/10">
                                  <th className="pb-1 pr-2 font-bold">{t('product')}</th>
                                  <th className="pb-1 pr-2 font-bold">{t('dosage')}</th>
                                  <th className="pb-1 font-bold">{t('group')}</th>
                                </tr>
                              </thead>
                              <tbody>
                                {result.chemical_reference.map((row, ri) => (
                                  <tr key={ri} className="border-t border-[#1A3626]/5">
                                    <td className="py-1.5 pr-2 text-[#1A3626] font-medium">{row.product}</td>
                                    <td className="py-1.5 pr-2 text-[#57695D]">{row.dosage}</td>
                                    <td className="py-1.5 text-[#57695D]">{row.group}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </motion.div>
              ) : (
                <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                  className="bg-[#FDFDFB] border border-[#1A3626]/10 rounded-2xl shadow-[4px_4px_10px_rgba(26,54,38,0.05),-4px_-4px_10px_rgba(255,255,255,1)] p-10 text-center h-full flex flex-col items-center justify-center"
                >
                  <div className="w-24 h-24 bg-[#E8E8E3] rounded-2xl flex items-center justify-center mb-5">
                    <ScanLine className="w-12 h-12 text-[#839E88]" strokeWidth={1} />
                  </div>
                  <p className="text-[#839E88] text-sm">{t('uploadAndDetect')}</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </motion.div>
    </Layout>
  );
};
