import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './App.css'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("React Error Boundary Caught Error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: '100vh',
          background: '#0B0F19',
          color: '#FFF',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '24px',
          fontFamily: 'Outfit, sans-serif'
        }}>
          <div style={{
            background: 'rgba(255, 51, 102, 0.1)',
            border: '1px solid #FF3366',
            borderRadius: '16px',
            padding: '32px',
            maxWidth: '500px',
            textAlign: 'center'
          }}>
            <h2 style={{ color: '#FF3366', marginBottom: '12px' }}>⚠️ VoluMetric Terminal Recovery</h2>
            <p style={{ color: '#94A3B8', fontSize: '0.9rem', marginBottom: '20px' }}>
              An unexpected render error occurred. Please click below to reset the terminal workspace.
            </p>
            <button
              onClick={() => { localStorage.clear(); window.location.reload(); }}
              style={{
                background: '#00F5A0',
                color: '#0B0F19',
                border: 'none',
                padding: '12px 24px',
                borderRadius: '8px',
                fontWeight: 700,
                cursor: 'pointer'
              }}
            >
              Reset & Reload Terminal
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>,
)
