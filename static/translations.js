// ============================================
// MULTI-LANGUAGE SUPPORT (English + Telugu)
// ============================================

const translations = {
    en: {
        // Navigation
        'nav_home': 'Home',
        'nav_scan': 'Scan Eye',
        'nav_assistant': 'AI Assistant',
        'nav_hospitals': 'Hospitals',
        'nav_vision': 'Vision Test',
        'nav_appointments': 'Appointments',
        'nav_history': 'History',
        'nav_login': 'Login',
        'nav_register': 'Register',
        'nav_logout': 'Logout',
        'nav_admin': 'Admin',
        
        // Common
        'welcome': 'Welcome to Hyphema Detection System',
        'scan_now': 'Scan Your Eye Now',
        'analyze': 'Analyze',
        'results': 'Results',
        'save': 'Save',
        'cancel': 'Cancel',
        'confirm': 'Confirm',
        'back': 'Back',
        'next': 'Next',
        
        // Results
        'prediction': 'Prediction',
        'confidence': 'Confidence',
        'severity': 'Severity',
        'normal': 'Normal',
        'mild': 'Mild',
        'moderate': 'Moderate',
        'severe': 'Severe',
        'critical': 'Critical',
        
        // Recommendations
        'recommendations': 'Recommendations',
        'immediate_action': 'Immediate Action',
        'care_instructions': 'Care Instructions',
        'disclaimer': 'This is an AI-generated recommendation. Please consult a medical professional.',
        
        // Vision Test
        'vision_test': 'Vision Screening Test',
        'cover_left_eye': 'Cover your LEFT eye',
        'cover_right_eye': 'Cover your RIGHT eye',
        'read_letters': 'Read the letters shown below',
        'vision_score': 'Vision Score',
        'normal_vision': 'Normal Vision',
        'mild_impairment': 'Mild Vision Impairment',
        'moderate_impairment': 'Moderate Vision Impairment',
        'severe_impairment': 'Severe Vision Impairment',
        
        // Appointments
        'book_appointment': 'Book Appointment',
        'select_hospital': 'Select Hospital',
        'select_date': 'Select Date',
        'select_time': 'Select Time',
        'patient_name': 'Patient Name',
        'patient_email': 'Email',
        'patient_phone': 'Phone Number',
        
        // Emergency
        'emergency': 'EMERGENCY',
        'seek_immediate_care': 'Seek Immediate Medical Attention',
        'call_emergency': 'Call Emergency Services'
    },
    
    te: {
        // Navigation
        'nav_home': 'హోమ్',
        'nav_scan': 'కంటి స్కాన్',
        'nav_assistant': 'AI సహాయకుడు',
        'nav_hospitals': 'ఆసుపత్రులు',
        'nav_vision': 'దృష్టి పరీక్ష',
        'nav_appointments': 'అపాయింట్మెంట్లు',
        'nav_history': 'చరిత్ర',
        'nav_login': 'లాగిన్',
        'nav_register': 'నమోదు చేయండి',
        'nav_logout': 'నిష్క్రమించు',
        'nav_admin': 'నిర్వాహకుడు',
        
        // Common
        'welcome': 'హైఫేమా డిటెక్షన్ సిస్టమ్‌కు స్వాగతం',
        'scan_now': 'ఇప్పుడు మీ కంటిని స్కాన్ చేయండి',
        'analyze': 'విశ్లేషించండి',
        'results': 'ఫలితాలు',
        'save': 'సేవ్ చేయండి',
        'cancel': 'రద్దు చేయండి',
        'confirm': 'నిర్ధారించండి',
        'back': 'వెనుకకు',
        'next': 'తదుపరి',
        
        // Results
        'prediction': 'అంచనా',
        'confidence': 'విశ్వాసం',
        'severity': 'తీవ్రత',
        'normal': 'సాధారణం',
        'mild': 'తేలికపాటి',
        'moderate': 'మధ్యస్థం',
        'severe': 'తీవ్రమైన',
        'critical': 'క్లిష్టమైన',
        
        // Recommendations
        'recommendations': 'సిఫార్సులు',
        'immediate_action': 'తక్షణ చర్య',
        'care_instructions': 'సంరక్షణ సూచనలు',
        'disclaimer': 'ఇది AI-ఉత్పత్తి చేసిన సిఫార్సు. దయచేసి వైద్య నిపుణుడిని సంప్రదించండి.',
        
        // Vision Test
        'vision_test': 'దృష్టి పరీక్ష',
        'cover_left_eye': 'మీ ఎడమ కన్ను కప్పండి',
        'cover_right_eye': 'మీ కుడి కన్ను కప్పండి',
        'read_letters': 'క్రింద చూపిన అక్షరాలు చదవండి',
        'vision_score': 'దృష్టి స్కోరు',
        'normal_vision': 'సాధారణ దృష్టి',
        'mild_impairment': 'తేలికపాటి దృష్టి లోపం',
        'moderate_impairment': 'మధ్యస్థ దృష్టి లోపం',
        'severe_impairment': 'తీవ్రమైన దృష్టి లోపం',
        
        // Appointments
        'book_appointment': 'అపాయింట్మెంట్ బుక్ చేయండి',
        'select_hospital': 'ఆసుపత్రిని ఎంచుకోండి',
        'select_date': 'తేదీని ఎంచుకోండి',
        'select_time': 'సమయం ఎంచుకోండి',
        'patient_name': 'రోగి పేరు',
        'patient_email': 'ఇమెయిల్',
        'patient_phone': 'ఫోన్ నంబర్',
        
        // Emergency
        'emergency': 'అత్యవసరం',
        'seek_immediate_care': 'తక్షణ వైద్య సహాయం తీసుకోండి',
        'call_emergency': 'అత్యవసర సేవలకు కాల్ చేయండి'
    }
};

let currentLang = 'en';

function setLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('language', lang);
    
    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.dataset.i18n;
        if (translations[lang] && translations[lang][key]) {
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = translations[lang][key];
            } else {
                element.textContent = translations[lang][key];
            }
        }
    });
    
    showToast(`Language changed to ${lang === 'en' ? 'English' : 'తెలుగు'}`, 'success');
}

// Load saved language preference
document.addEventListener('DOMContentLoaded', () => {
    const savedLang = localStorage.getItem('language') || 'en';
    setLanguage(savedLang);
});