import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  en: {
    translation: {
      // Navigation
      dashboard: 'Dashboard',
      history: 'History',
      diseases: 'Disease Library',
      admin: 'Admin Panel',
      logout: 'Logout',
      
      // Auth
      login: 'Login',
      register: 'Register',
      username: 'Username',
      password: 'Password',
      loginButton: 'Login',
      registerButton: 'Register',
      alreadyHaveAccount: 'Already have an account?',
      dontHaveAccount: "Don't have an account?",
      
      // Profile
      completeProfile: 'Complete Your Profile',
      name: 'Name',
      mobile: 'Mobile Number',
      saveProfile: 'Save Profile',
      
      // Dashboard
      uploadImage: 'Upload Sugarcane Image',
      takePhoto: 'Take Photo',
      dragDrop: 'Drag and drop an image here, or click to select',
      analyzing: 'Analyzing...',
      detectDisease: 'Detect Disease',
      dashboardSubtitle: 'Upload or capture a sugarcane leaf image for disease analysis',
      submittedForReview: 'Submitted for Review',
      submittedMsg: 'Your scan has been submitted. An admin will review the results and may add suggestions. You will see the full diagnosis once it is approved.',
      aiAnalyzed: 'AI has analyzed your image. Waiting for admin verification.',
      uploadAndDetect: 'Upload an image and click detect to see results',
      newScan: 'New Scan',
      
      // Results
      diseaseDetected: 'Disease Detected',
      confidence: 'Confidence',
      severity: 'Severity',
      high: 'High',
      medium: 'Medium',
      low: 'Low',
      treatment: 'Treatment',
      recommendedProducts: 'Recommended Products / Fertilizers',
      symptoms: 'Symptoms',
      causes: 'Causes',
      prevention: 'Prevention',
      
      // History
      scanHistory: 'Scan History',
      noHistory: 'No scan history yet',
      date: 'Date',
      disease: 'Disease',
      historySubtitle: 'View your submitted scans and approved results',
      searchPlaceholder: 'Search by disease or status...',
      awaitingReview: 'Awaiting Review',
      approved: 'Approved',
      rejected: 'Rejected',
      pendingReview: 'Pending Review',
      pendingMsg: 'Your scan is being reviewed by an admin...',
      rejectedMsg: 'This scan was rejected by the admin.',
      adminSuggestion: 'Admin Suggestion',
      adminNote: 'Admin Note',
      scanRejected: 'Scan Rejected',
      unrecognizedDisease: 'Disease Not Yet Supported',
      unrecognizedMsg: 'This disease is not yet in our detection model. Admin will review your scan and provide suggestions.',
      
      // Admin
      totalUsers: 'Total Users',
      totalScans: 'Total Scans',
      diseaseDistribution: 'Disease Distribution',
      recentScans: 'Recent Scans',
      user: 'User',
      
      // Common
      loading: 'Loading...',
      error: 'Error',
      success: 'Success'
    }
  },
  hi: {
    translation: {
      // Navigation
      dashboard: 'डैशबोर्ड',
      history: 'इतिहास',
      diseases: 'रोग पुस्तकालय',
      admin: 'प्रशासन पैनल',
      logout: 'लॉग आउट',
      
      // Auth
      login: 'लॉग इन',
      register: 'पंजीकरण',
      username: 'उपयोगकर्ता नाम',
      password: 'पासवर्ड',
      loginButton: 'लॉग इन करें',
      registerButton: 'पंजीकरण करें',
      alreadyHaveAccount: 'पहले से खाता है?',
      dontHaveAccount: 'खाता नहीं है?',
      
      // Profile
      completeProfile: 'अपना प्रोफ़ाइल पूरा करें',
      name: 'नाम',
      mobile: 'मोबाइल नंबर',
      saveProfile: 'प्रोफ़ाइल सहेजें',
      
      // Dashboard
      uploadImage: 'गन्ने की छवि अपलोड करें',
      takePhoto: 'फोटो लें',
      dragDrop: 'यहां एक छवि खींचें और छोड़ें, या चुनने के लिए क्लिक करें',
      analyzing: 'विश्लेषण कर रहा है...',
      detectDisease: 'रोग का पता लगाएं',
      dashboardSubtitle: 'रोग विश्लेषण के लिए गन्ने की पत्ती की छवि अपलोड या कैप्चर करें',
      submittedForReview: 'समीक्षा के लिए भेजा गया',
      submittedMsg: 'आपका स्कैन भेज दिया गया है। एक व्यवस्थापक परिणामों की समीक्षा करेगा। अनुमोदन के बाद आपको पूर्ण निदान दिखाई देगा।',
      aiAnalyzed: 'AI ने आपकी छवि का विश्लेषण कर लिया है। व्यवस्थापक सत्यापन की प्रतीक्षा है।',
      uploadAndDetect: 'छवि अपलोड करें और परिणाम देखने के लिए क्लिक करें',
      newScan: 'नया स्कैन',
      
      // Results
      diseaseDetected: 'रोग का पता चला',
      confidence: 'विश्वास',
      severity: 'गंभीरता',
      high: 'उच्च',
      medium: 'मध्यम',
      low: 'कम',
      treatment: 'उपचार',
      recommendedProducts: 'अनुशंसित उत्पाद / उर्वरक',
      symptoms: 'लक्षण',
      causes: 'कारण',
      prevention: 'रोकथाम',
      
      // History
      scanHistory: 'स्कैन इतिहास',
      noHistory: 'अभी तक कोई स्कैन इतिहास नहीं',
      date: 'तारीख',
      disease: 'रोग',
      historySubtitle: 'अपने सबमिट किए गए स्कैन और अनुमोदित परिणाम देखें',
      searchPlaceholder: 'रोग या स्थिति से खोजें...',
      awaitingReview: 'समीक्षा की प्रतीक्षा',
      approved: 'अनुमोदित',
      rejected: 'अस्वीकृत',
      pendingReview: 'लंबित समीक्षा',
      pendingMsg: 'आपका स्कैन व्यवस्थापक द्वारा समीक्षा किया जा रहा है...',
      rejectedMsg: 'यह स्कैन व्यवस्थापक द्वारा अस्वीकृत किया गया।',
      adminSuggestion: 'व्यवस्थापक सुझाव',
      adminNote: 'व्यवस्थापक टिप्पणी',
      scanRejected: 'स्कैन अस्वीकृत',
      unrecognizedDisease: 'रोग अभी तक समर्थित नहीं',
      unrecognizedMsg: 'यह रोग अभी तक हमारे मॉडल में नहीं है। प्रशासक आपकी स्कैन की समीक्षा करेंगे और सुझाव देंगे।',
      
      // Admin
      totalUsers: 'कुल उपयोगकर्ता',
      totalScans: 'कुल स्कैन',
      diseaseDistribution: 'रोग वितरण',
      recentScans: 'हाल के स्कैन',
      user: 'उपयोगकर्ता',
      
      // Common
      loading: 'लोड हो रहा है...',
      error: 'त्रुटि',
      success: 'सफलता'
    }
  },
  mr: {
    translation: {
      // Navigation
      dashboard: 'डॅशबोर्ड',
      history: 'इतिहास',
      diseases: 'रोग ग्रंथालय',
      admin: 'प्रशासन पॅनेल',
      logout: 'लॉग आउट',
      
      // Auth
      login: 'लॉगिन',
      register: 'नोंदणी',
      username: 'वापरकर्ता नाव',
      password: 'पासवर्ड',
      loginButton: 'लॉगिन करा',
      registerButton: 'नोंदणी करा',
      alreadyHaveAccount: 'आधीच खाते आहे?',
      dontHaveAccount: 'खाते नाही?',
      
      // Profile
      completeProfile: 'तुमचे प्रोफाइल पूर्ण करा',
      name: 'नाव',
      mobile: 'मोबाईल नंबर',
      saveProfile: 'प्रोफाइल जतन करा',
      
      // Dashboard
      uploadImage: 'ऊस प्रतिमा अपलोड करा',
      takePhoto: 'फोटो काढा',
      dragDrop: 'येथे प्रतिमा ओढा आणि सोडा, किंवा निवडण्यासाठी क्लिक करा',
      analyzing: 'विश्लेषण करत आहे...',
      detectDisease: 'रोग शोधा',
      dashboardSubtitle: 'रोग विश्लेषणासाठी ऊसाच्या पानाची प्रतिमा अपलोड करा किंवा काढा',
      submittedForReview: 'पुनरावलोकनासाठी सबमिट केले',
      submittedMsg: 'तुमचा स्कॅन सबमिट केला आहे. प्रशासक निकालांचे पुनरावलोकन करतील आणि सूचना जोडू शकतात. मंजूर झाल्यानंतर तुम्हाला पूर्ण निदान दिसेल.',
      aiAnalyzed: 'AI ने तुमच्या प्रतिमेचे विश्लेषण केले आहे. प्रशासक पडताळणीची वाट पाहत आहे.',
      uploadAndDetect: 'प्रतिमा अपलोड करा आणि निकाल पाहण्यासाठी शोधा वर क्लिक करा',
      newScan: 'नवीन स्कॅन',
      
      // Results
      diseaseDetected: 'रोग आढळला',
      confidence: 'विश्वास',
      severity: 'तीव्रता',
      high: 'उच्च',
      medium: 'मध्यम',
      low: 'कमी',
      treatment: 'उपचार',
      recommendedProducts: 'शिफारस केलेली उत्पादने / खते',
      symptoms: 'लक्षणे',
      causes: 'कारणे',
      prevention: 'प्रतिबंध',
      
      // History
      scanHistory: 'स्कॅन इतिहास',
      noHistory: 'अद्याप कोणताही स्कॅन इतिहास नाही',
      date: 'तारीख',
      disease: 'रोग',
      historySubtitle: 'तुमचे सबमिट केलेले स्कॅन आणि मंजूर निकाल पहा',
      searchPlaceholder: 'रोग किंवा स्थितीनुसार शोधा...',
      awaitingReview: 'पुनरावलोकनाची वाट',
      approved: 'मंजूर',
      rejected: 'नाकारले',
      pendingReview: 'प्रलंबित पुनरावलोकन',
      pendingMsg: 'तुमचा स्कॅन प्रशासकाद्वारे पुनरावलोकन केला जात आहे...',
      rejectedMsg: 'हा स्कॅन प्रशासकाने नाकारला.',
      adminSuggestion: 'प्रशासक सूचना',
      adminNote: 'प्रशासक टीप',
      scanRejected: 'स्कॅन नाकारला',
      unrecognizedDisease: 'रोग अद्याप समर्थित नाही',
      unrecognizedMsg: 'हा रोग अद्याप आमच्या मॉडेलमध्ये नाही. प्रशासक तुमचा स्कॅन पाहतील आणि सूचना देतील.',
      
      // Admin
      totalUsers: 'एकूण वापरकर्ते',
      totalScans: 'एकूण स्कॅन',
      diseaseDistribution: 'रोग वितरण',
      recentScans: 'अलीकडील स्कॅन',
      user: 'वापरकर्ता',
      
      // Common
      loading: 'लोड होत आहे...',
      error: 'त्रुटी',
      success: 'यश'
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'en',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
