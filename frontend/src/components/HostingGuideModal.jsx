import React from 'react';
import { X, Server, Globe, Terminal, CheckCircle2 } from 'lucide-react';

export default function HostingGuideModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '1.2rem', fontWeight: 700 }}>
            <Globe color="var(--accent-green)" size={24} />
            Live Deployment & Hosting Guide (होस्टिंग गाइड)
          </div>
          <button className="btn" onClick={onClose} style={{ padding: '6px' }}><X size={18} /></button>
        </div>

        <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
          इस प्रोजेक्ट को 100% फ्री में क्लाउड (Vercel & Render) पर लाइव होस्ट करने के लिए निम्नलिखित चरणों का पालन करें:
        </p>

        {/* Step 1: Backend hosting */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <h4 style={{ color: 'var(--accent-gold)', display: 'flex', alignItems: 'center', gap: 6 }}>
            <Server size={18} /> Step 1: Host Backend on Render (Free Python Hosting)
          </h4>
          <ol style={{ paddingLeft: 20, fontSize: '0.85rem', color: 'var(--text-main)', lineHeight: '1.6' }}>
            <li>अपने <code>backend/</code> कोड को GitHub पर पुश (Push) करें।</li>
            <li><a href="https://render.com" target="_blank" rel="noreferrer" style={{ color: 'var(--accent-blue)' }}>Render.com</a> पर अकाउंट बनाएं और <strong>New Web Service</strong> चुनें।</li>
            <li>Build Command दर्ज करें: <code>pip install -r requirements.txt</code></li>
            <li>Start Command दर्ज करें: <code>uvicorn main:app --host 0.0.0.0 --port $PORT</code></li>
            <li>आपकी backend API URL तैयार हो जाएगी (जैसे: <code>https://volume-backend.onrender.com</code>)।</li>
          </ol>
        </div>

        {/* Step 2: Frontend hosting */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <h4 style={{ color: 'var(--accent-green)', display: 'flex', alignItems: 'center', gap: 6 }}>
            <Globe size={18} /> Step 2: Host Frontend on Vercel
          </h4>
          <ol style={{ paddingLeft: 20, fontSize: '0.85rem', color: 'var(--text-main)', lineHeight: '1.6' }}>
            <li><a href="https://vercel.com" target="_blank" rel="noreferrer" style={{ color: 'var(--accent-blue)' }}>Vercel.com</a> पर जाएँ और <code>frontend</code> फोल्डर कनेक्ट करें।</li>
            <li>Environment Variable ऐड करें: <code>VITE_API_URL = https://volume-backend.onrender.com</code></li>
            <li>Deploy बटन पर क्लिक करें। आपका लाइव प्रोजेक्ट तैयार हो जाएगा!</li>
          </ol>
        </div>

        {/* Step 3: Docker execution */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <h4 style={{ color: 'var(--accent-purple)', display: 'flex', alignItems: 'center', gap: 6 }}>
            <Terminal size={18} /> Local / Docker Execution
          </h4>
          <div className="code-block">
            docker-compose up --build
          </div>
        </div>

        <div style={{ textAlign: 'right', marginTop: '10px' }}>
          <button className="btn btn-primary" onClick={onClose}>
            <CheckCircle2 size={16} /> Got it!
          </button>
        </div>
      </div>
    </div>
  );
}
