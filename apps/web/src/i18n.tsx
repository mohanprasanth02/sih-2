import React, { createContext, useContext, useState, useEffect } from 'react';

export type Language = 'en' | 'hi';

interface I18nContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const translations: Record<Language, Record<string, string>> = {
  en: {
    // Header & Brand
    app_title_oiml: 'LEGAL METROLOGY • OIML R 76',
    app_badge_oiml: 'PATTERN EVALUATION',
    app_title_labelguard: 'LABELGUARD AI',
    app_badge_labelguard: 'RULES 2011',
    header_subtitle_oiml: 'Non-Automatic Weighing Instruments Verification • Legal Metrology Act, 2009',
    header_subtitle_labelguard: 'Packaged Commodities Automated Compliance System',
    nawi_module_btn: 'NAWI Model Approval (OIML R 76)',
    packaged_module_btn: 'Packaged Commodities (Rules 2011)',
    core_status: 'Core:',

    // Roles
    role_inspector: 'Inspector',
    role_supervisor: 'Supervisor',
    role_admin: 'Admin',
    role_viewer: 'Viewer',

    // Sidebar Navigation
    nav_nawi_dashboard: 'NAWI Dashboard',
    nav_new_evaluation: 'New Type Evaluation',
    nav_reports_history: 'Reports & History',
    nav_standards_explorer: 'OIML Standards Explorer',
    nav_dashboard: 'Dashboard',
    nav_verify_product: 'Verify Product',
    nav_inspections: 'Inspections',
    nav_review_queue: 'Review Queue',
    nav_rules_playground: 'Rules & Playground',
    nav_analytics: 'Analytics & Maps',
    nav_mobile_sim: 'Mobile Scanner Demo',
    nav_ai_models: 'AI Model Telemetry',
    statutory_authority: 'Statutory Authority',
    statutory_footnote_oiml: 'Enforced under Section 22 of Legal Metrology Act, 2009 & OIML Recommendation R 76-1:2006.',
    statutory_footnote_labelguard: 'Enforced under Legal Metrology Act, 2009 & (Packaged Commodities) Rules, 2011.',

    // Hero & Dashboard (NAWI)
    hero_badge: 'Digital Pattern Evaluation v2.0 is now live',
    hero_title: 'Automate legal metrology that ensures trust',
    hero_subtitle: 'Automated test data recording, compliance evaluation against Table 6 Maximum Permissible Error (MPE) thresholds, and instant pattern approval report generation under the Legal Metrology Act, 2009.',
    btn_start_evaluation: 'Start Type Evaluation',
    btn_explore_standards: 'Explore Standards & MPE',
    btn_load_samples: 'Load Sample Data',
    terminal_title: 'Pattern Evaluation Test Bench',
    active_scale_params: 'ACTIVE SCALE PARAMETERS:',
    digital_readout: 'DIGITAL LOAD CELL READOUT',
    verified: 'VERIFIED',
    trusted_by: 'DESIGNED FOR STATUTORY LEGAL METROLOGY LABORATORIES',
    modular_title: 'Modular Metrological Intelligence',
    modular_subtitle: 'Comprehensive compliance verification modules adhering to international metrological standards.',
    card_weighing_title: 'Weighing Performance (A.4.4)',
    card_weighing_desc: 'Step-by-step loading and unloading test with flash-point changeover formulas for true rounded indication error.',
    card_weighing_link: 'Explore Weighing Test',
    card_repeat_title: 'Repeatability & Eccentricity',
    card_repeat_desc: 'Off-center quadrant loading (Clause A.4.7) and 10-cycle repeatability evaluations under Clauses A.4.10.',
    card_repeat_link: 'Explore Repeatability',
    card_reports_title: 'Standardized Reports (R 76-2)',
    card_reports_desc: 'Generate official pattern evaluation certificates in printable PDF with National Crest and editable Word (.docx).',
    card_reports_link: 'View Report Archive',
    recent_evaluations: 'Recent Pattern Evaluation Records',
    recent_evaluations_sub: 'Live database records maintained under Directorate of Legal Metrology',
    search_evaluations: 'Search evaluations...',
    seed_btn: 'Seed Sample Instruments',

    // Table Headers & Statuses
    th_report: 'REPORT #',
    th_model: 'MODEL / INSTRUMENT',
    th_manufacturer: 'MANUFACTURER',
    th_accuracy_class: 'ACCURACY CLASS',
    th_capacity: 'CAPACITY (Max)',
    th_status: 'STATUS',
    th_exports: 'EXPORTS',
    compliant: 'COMPLIANT',
    testing_in_progress: 'TESTING IN PROGRESS',
    rejected: 'REJECTED',
    status_passed: 'PASSED',
    status_violations: 'VIOLATIONS DETECTED',
    status_review_needed: 'REVIEW NEEDED',

    // Wizard
    wizard_title: 'Test Observation & Error Compliance Engine',
    wizard_subtitle: 'Automated MPE Table 6 calculation with flash-point changeover formulas',
    btn_recalculate: 'Recalculate Metrology',
    btn_back: 'Back',
    btn_prev_step: 'Previous Step',
    btn_next_step: 'Next Step',
    btn_finalize_save: 'Finalize & Save',
    step_1: 'Instrument Specs',
    step_2: 'Lab Conditions',
    step_3: 'Weighing Test (A.4.4)',
    step_4: 'Repeat & Eccentricity',
    step_5: 'Review & Certification',
    permissible_range: 'PERMISSIBLE RANGE [100 to 10,000]',
    exceeds_range: 'EXCEEDS CLASS RANGE',
    auto_populate_points: 'Auto-Populate OIML Load Points',
    save_certify_btn: 'Save & Certify Model Approval',

    // Repository
    repo_title: 'Type Evaluation Archive & Pattern Approvals',
    repo_subtitle: 'Retrieve records, inspect test batteries, verify digital signatures, and export official reports.',
    export_pdf: 'Export PDF',
    export_docx: 'Export Word (.docx)',
    digitally_sign: 'Digitally Sign',
    digitally_certified: 'DIGITALLY CERTIFIED',

    // Rules Playground
    rules_title: 'Legal Metrology (Packaged Commodities) Rules, 2011',
    rules_sub: 'Codified statutory rules, mandatory declarations, and deterministic rule engine simulator',
    rules_tool_title: 'Deterministic Rule Testing Playground',
    rules_tool_sub: 'Input test declarations to verify deterministic rule engine decisions without uploading images',
    rules_test_btn: 'TEST RULES DETERMINISTICALLY',
    rules_evaluating: 'Evaluating...',
    rules_category: 'Product Category',
    rules_product_name: 'Product Name',
    rules_net_qty: 'Net Quantity Declaration',
    rules_mrp: 'Retail Sale Price (MRP)',
    rules_usp: 'Unit Sale Price (USP)',
    rules_mfg: 'Manufacturer / Packer',
    rules_origin: 'Country of Origin',
    rules_date: 'Month & Year of Mfg/Pkg',
    rules_care: 'Consumer Care Details',
    rules_codified_list: 'Codified Statutory Rules (Legal Metrology Rules 2011)',
    rules_result_title: 'Rule Engine Compliance Evaluation Result',

    // AI Models Telemetry
    ai_telemetry_title: 'AI Pipeline Infrastructure',
    ai_telemetry_sub: 'Real-time metrics for computer vision, optical character recognition, and rule validation services',
    ai_fastapi: 'FastAPI Gateway',
    ai_db: 'Database Engine',
    ai_storage: 'Evidence Storage',
    ai_engine: 'Compliance Engine',
    ai_operational: 'Operational',
    ai_connected: 'Connected',
    ai_encrypted: 'Encrypted',
    ai_deterministic: 'Deterministic',
    ai_active_components: 'Active Computer Vision & AI Components',
    ai_model_name: 'MODEL / SERVICE',
    ai_type: 'ARCHITECTURE',
    ai_latency: 'AVG LATENCY',
    ai_status: 'HEALTH STATUS',

    // Mobile Simulator
    mobile_sim_title: 'Field Mobile Scanner Simulation',
    mobile_sim_sub: 'Simulate on-device camera guidance, edge blur/lighting detection, and multi-surface inspection capture',
    mobile_step_setup: 'Setup Inspection',
    mobile_step_camera: 'Camera Capture',
    mobile_step_processing: 'Pipeline Processing',
    mobile_step_completed: 'Inspection Completed',
    mobile_btn_start: 'Launch Camera Inspection',
    mobile_btn_capture: 'Capture Current Surface',
    mobile_btn_reset: 'Reset Simulator',
    mobile_view_report: 'View Inspection Report',

    // Verify Product
    verify_title: 'Automated Package Compliance Verification',
    verify_sub: 'Upload product surface images or capture live labels for OCR extraction and statutory verification',
    verify_drop_title: 'Upload Multi-Surface Packaging Imagery',
    verify_start_btn: 'Run AI Verification Pipeline',
  },
  hi: {
    // Header & Brand
    app_title_oiml: 'विधिक मापविज्ञान • OIML R 76',
    app_badge_oiml: 'मॉडल अनुमोदन',
    app_title_labelguard: 'लेबल गार्ड AI',
    app_badge_labelguard: 'नियम 2011',
    header_subtitle_oiml: 'गैर-स्वचालित तौल उपकरण सत्यापन • विधिक मापविज्ञान अधिनियम, 2009',
    header_subtitle_labelguard: 'पैकेज्ड कमोडिटी स्वचालित अनुपालन प्रणाली',
    nawi_module_btn: 'NAWI मॉडल अनुमोदन (OIML R 76)',
    packaged_module_btn: 'पैकेज्ड कमोडिटी (नियम 2011)',
    core_status: 'कोर स्थिति:',

    // Roles
    role_inspector: 'निरीक्षक',
    role_supervisor: 'पर्यवेक्षक',
    role_admin: 'प्रशासक',
    role_viewer: 'दर्शक (Viewer)',

    // Sidebar Navigation
    nav_nawi_dashboard: 'NAWI डैशबोर्ड',
    nav_new_evaluation: 'नया मॉडल मूल्यांकन',
    nav_reports_history: 'रिपोर्ट और इतिहास',
    nav_standards_explorer: 'OIML मानक एक्सप्लोरर',
    nav_dashboard: 'डैशबोर्ड',
    nav_verify_product: 'उत्पाद सत्यापन',
    nav_inspections: 'निरीक्षण सूची',
    nav_review_queue: 'समीक्षा कतार',
    nav_rules_playground: 'नियम एवं प्लेग्राउंड',
    nav_analytics: 'एनालिटिक्स एवं मानचित्र',
    nav_mobile_sim: 'मोबाइल स्कैनर डेमो',
    nav_ai_models: 'AI मॉडल टेलीमेट्री',
    statutory_authority: 'वैधानिक अधिकार',
    statutory_footnote_oiml: 'विधिक मापविज्ञान अधिनियम, 2009 की धारा 22 एवं OIML अनुशंसा R 76-1:2006 के तहत लागू।',
    statutory_footnote_labelguard: 'विधिक मापविज्ञान अधिनियम, 2009 एवं पैकेज्ड कमोडिटीज नियम, 2011 के तहत प्रवर्तित।',

    // Hero & Dashboard (NAWI)
    hero_badge: 'डिजिटल मॉडल अनुमोदन v2.0 अब उपलब्ध है',
    hero_title: 'कानूनी मापविज्ञान का स्वचालित एवं विश्वसनीय प्रमाणीकरण',
    hero_subtitle: 'परीक्षण डेटा का स्वचालित अंकन, तालिका 6 अधिकतम अनुमेय त्रुटि (MPE) सीमाओं की त्वरित जांच, और विधिक मापविज्ञान अधिनियम, 2009 के तहत आधिकारिक रिपोर्ट तैयार करना।',
    btn_start_evaluation: 'मॉडल मूल्यांकन शुरू करें',
    btn_explore_standards: 'मानक एवं MPE देखें',
    btn_load_samples: 'नमूना डेटा लोड करें',
    terminal_title: 'मॉडल मूल्यांकन परीक्षण बेंच',
    active_scale_params: 'सक्रिय तौल मापदंड:',
    digital_readout: 'डिजिटल लोड सेल डिस्प्ले',
    verified: 'प्रमाणित',
    trusted_by: 'मान्यता प्राप्त विधिक मापविज्ञान प्रयोगशालाओं के लिए समर्पित',
    modular_title: 'माड्यूलर मापविज्ञान बुद्धिमत्ता',
    modular_subtitle: 'अंतरराष्ट्रीय मानकों (OIML R 76-1:2006) के अनुरूप संपूर्ण अनुपालन सत्यापन मॉड्यूल।',
    card_weighing_title: 'तौल निष्पादन परीक्षण (A.4.4)',
    card_weighing_desc: 'सटीक त्रुटि गणना के लिए फ्लैश-पॉइंट चेंजओवर फॉर्मूले के साथ भार वर्धन और कमी परीक्षण।',
    card_weighing_link: 'तौल परीक्षण देखें',
    card_repeat_title: 'पुनरावृत्ति एवं उत्केंद्रता',
    card_repeat_desc: 'कोने का भार (धारा A.4.7) एवं 10-चक्र पुनरावृत्ति परीक्षण (धारा A.4.10) का संपूर्ण विश्लेषण।',
    card_repeat_link: 'पुनरावृत्ति देखें',
    card_reports_title: 'मानकीकृत रिपोर्ट (R 76-2)',
    card_reports_desc: 'राष्ट्रीय प्रतीक चिन्ह के साथ आधिकारिक पीडीएफ और संपादन योग्य वर्ड (.docx) रिपोर्ट तैयार करें।',
    card_reports_link: 'रिपोर्ट संग्रह देखें',
    recent_evaluations: 'हाल के मॉडल अनुमोदन रिकॉर्ड',
    recent_evaluations_sub: 'विधिक मापविज्ञान निदेशालय के अंतर्गत सुरक्षित डिजिटल रिकॉर्ड',
    search_evaluations: 'मूल्यांकन खोजें...',
    seed_btn: 'नमूना उपकरण लोड करें',

    // Table Headers & Statuses
    th_report: 'रिपोर्ट संख्या',
    th_model: 'मॉडल / उपकरण',
    th_manufacturer: 'निर्माता',
    th_accuracy_class: 'सटीकता वर्ग',
    th_capacity: 'क्षमता (Max)',
    th_status: 'स्थिति',
    th_exports: 'निर्यात',
    compliant: 'अनुरूप (सफल)',
    testing_in_progress: 'परीक्षण जारी',
    rejected: 'अस्वीकृत',
    status_passed: 'उत्तीर्ण (सफल)',
    status_violations: 'उल्लंघन दर्ज',
    status_review_needed: 'समीक्षा आवश्यक',

    // Wizard
    wizard_title: 'परीक्षण अवलोकन एवं त्रुटि अनुपालन इंजन',
    wizard_subtitle: 'फ्लैश-पॉइंट सूत्रों के साथ OIML तालिका 6 MPE का स्वचालित परिकलन',
    btn_recalculate: 'मापविज्ञान पुनर्गणना',
    btn_back: 'वापस',
    btn_prev_step: 'पिछला चरण',
    btn_next_step: 'अगला चरण',
    btn_finalize_save: 'सत्यापित एवं सुरक्षित करें',
    step_1: 'उपकरण विवरण',
    step_2: 'प्रयोगशाला स्थिति',
    step_3: 'तौल परीक्षण (A.4.4)',
    step_4: 'पुनरावृत्ति एवं उत्केंद्रता',
    step_5: 'समीक्षा एवं प्रमाणीकरण',
    permissible_range: 'अनुमेय सीमा [100 से 10,000]',
    exceeds_range: 'अनुमेय सीमा से बाहर',
    auto_populate_points: 'OIML भार बिंदु स्वतः भरें',
    save_certify_btn: 'सुरक्षित करें एवं मॉडल अनुमोदित करें',

    // Repository
    repo_title: 'मॉडल मूल्यांकन संग्रह एवं अनुमोदन',
    repo_subtitle: 'परीक्षण रिकॉर्ड देखें, डिजिटल हस्ताक्षर सत्यापित करें, और आधिकारिक रिपोर्ट डाउनलोड करें।',
    export_pdf: 'पीडीएफ निर्यात',
    export_docx: 'वर्ड (.docx) निर्यात',
    digitally_sign: 'डिजिटल हस्ताक्षर करें',
    digitally_certified: 'डिजिटल रूप से प्रमाणित',

    // Rules Playground
    rules_title: 'विधिक मापविज्ञान (पैकेज्ड कमोडिटीज) नियम, 2011',
    rules_sub: 'संहिताबद्ध वैधानिक नियम, अनिवार्य घोषणाएं, और प्रत्यक्ष नियम सत्यापन सिम्युलेटर',
    rules_tool_title: 'नियम परीक्षण टूल (बिना छवि के)',
    rules_tool_sub: 'छवि अपलोड किए बिना सीधे वैधानिक नियमों के आधार पर घोषणाओं का मूल्यांकन करें',
    rules_test_btn: 'नियमों का मूल्यांकन करें',
    rules_evaluating: 'मूल्यांकन जारी...',
    rules_category: 'उत्पाद श्रेणी',
    rules_product_name: 'उत्पाद का नाम',
    rules_net_qty: 'शुद्ध मात्रा की घोषणा',
    rules_mrp: 'अधिकतम खुदरा मूल्य (MRP)',
    rules_usp: 'इकाई विक्रय मूल्य (USP)',
    rules_mfg: 'निर्माता / पैकर विवरण',
    rules_origin: 'मूल देश (Country of Origin)',
    rules_date: 'निर्माण/पैकिंग का माह एवं वर्ष',
    rules_care: 'उपभोक्ता हेल्पलाइन विवरण',
    rules_codified_list: 'संहिताबद्ध वैधानिक नियम (नियम 2011)',
    rules_result_title: 'नियम इंजन अनुपालन परिणाम',

    // AI Models Telemetry
    ai_telemetry_title: 'AI पाइपलाइन इन्फ्रास्ट्रक्चर',
    ai_telemetry_sub: 'कंप्यूटर विज़न, ओसीआर एवं नियम सत्यापन सेवाओं की रियल-टाइम स्थिति',
    ai_fastapi: 'फास्टएपीआई गेटवे',
    ai_db: 'डेटाबेस इंजन',
    ai_storage: 'साक्ष्य संग्रहण',
    ai_engine: 'अनुपालन इंजन',
    ai_operational: 'सक्रिय (Operational)',
    ai_connected: 'कनेक्टेड (Connected)',
    ai_encrypted: 'सुरक्षित एवं एन्क्रिप्टेड',
    ai_deterministic: 'सटीक एवं संहिताबद्ध',
    ai_active_components: 'सक्रिय कंप्यूटर विज़न एवं AI घटक',
    ai_model_name: 'मॉडल / सेवा',
    ai_type: 'आर्किटेक्चर',
    ai_latency: 'औसत विलंबता',
    ai_status: 'स्वास्थ्य स्थिति',

    // Mobile Simulator
    mobile_sim_title: 'फील्ड मोबाइल स्कैनर सिमुलेटर',
    mobile_sim_sub: 'ऑन-डिवाइस कैमरा मार्गदर्शन, किनारा स्पष्टता, प्रकाश संवेदन एवं बहु-सतह कैप्चर',
    mobile_step_setup: 'निरीक्षण सेटअप',
    mobile_step_camera: 'कैमरा कैप्चर',
    mobile_step_processing: 'पाइपलाइन प्रोसेसिंग',
    mobile_step_completed: 'निरीक्षण पूर्ण',
    mobile_btn_start: 'कैमरा निरीक्षण प्रारंभ करें',
    mobile_btn_capture: 'वर्तमान सतह की फोटो लें',
    mobile_btn_reset: 'सिमुलेटर रीसेट करें',
    mobile_view_report: 'निरीक्षण रिपोर्ट देखें',

    // Verify Product
    verify_title: 'स्वचालित पैकेज अनुपालन सत्यापन',
    verify_sub: 'ओसीआर निष्कर्षण और वैधानिक सत्यापन के लिए उत्पाद सतह की तस्वीरें अपलोड करें या लाइव कैप्चर करें',
    verify_drop_title: 'पैकेजिंग की बहु-सतह छवियां अपलोड करें',
    verify_start_btn: 'AI सत्यापन पाइपलाइन चलाएं',
  }
};

const I18nContext = createContext<I18nContextType>({
  language: 'en',
  setLanguage: () => {},
  t: (key: string) => key,
});

export const I18nProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>(() => {
    const saved = localStorage.getItem('app_language');
    return (saved === 'hi' || saved === 'en') ? saved : 'en';
  });

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('app_language', lang);
  };

  const t = (key: string): string => {
    return translations[language]?.[key] || translations['en']?.[key] || key;
  };

  return (
    <I18nContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </I18nContext.Provider>
  );
};

export const useI18n = () => useContext(I18nContext);
