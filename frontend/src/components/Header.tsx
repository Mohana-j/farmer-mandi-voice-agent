import React from 'react';
import { Language } from '../types';
import { translations } from '../i18n/translations';
import { Activity, Globe, Sprout } from 'lucide-react';

interface HeaderProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  language: Language;
  setLanguage: (lang: Language) => void;
  sourceMode: 'synthetic' | 'live';
  isHealthy: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  currentTab,
  setCurrentTab,
  language,
  setLanguage,
  sourceMode,
  isHealthy,
}) => {
  const t = translations[language];

  return (
    <header className="app-header">
      <div className="header-top">
        <div className="brand-group">
          <div className="brand-icon">
            <Sprout size={28} color="#2e7d32" />
          </div>
          <div>
            <h1 className="brand-title">{t.appName}</h1>
            <p className="brand-tagline">{t.tagline}</p>
          </div>
        </div>

        <div className="header-status-controls">
          {/* Data Mode Badge */}
          <div className={`badge-mode ${sourceMode === 'live' ? 'mode-live' : 'mode-synthetic'}`}>
            <span className="dot-pulse"></span>
            <span>{sourceMode === 'live' ? t.modeLive : t.modeSynthetic}</span>
          </div>

          {/* Backend Health */}
          <div className={`health-pill ${isHealthy ? 'health-ok' : 'health-down'}`}>
            <Activity size={14} />
            <span>{isHealthy ? t.statusHealthy : t.statusConnecting}</span>
          </div>

          {/* Language Selector */}
          <div className="lang-switcher">
            <Globe size={16} />
            <button
              className={`btn-lang ${language === 'en' ? 'active' : ''}`}
              onClick={() => setLanguage('en')}
            >
              English
            </button>
            <span className="divider">|</span>
            <button
              className={`btn-lang ${language === 'ta' ? 'active' : ''}`}
              onClick={() => setLanguage('ta')}
            >
              தமிழ்
            </button>
          </div>
        </div>
      </div>

      {/* Navigation bar */}
      <nav className="header-nav">
        <button
          className={`nav-item ${currentTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setCurrentTab('dashboard')}
        >
          {t.navDashboard}
        </button>
        <button
          className={`nav-item ${currentTab === 'query' ? 'active' : ''}`}
          onClick={() => setCurrentTab('query')}
        >
          {t.navQuery}
        </button>
        <button
          className={`nav-item ${currentTab === 'comparison' ? 'active' : ''}`}
          onClick={() => setCurrentTab('comparison')}
        >
          {t.navComparison}
        </button>
        <button
          className={`nav-item ${currentTab === 'alerts' ? 'active' : ''}`}
          onClick={() => setCurrentTab('alerts')}
        >
          {t.navAlerts}
        </button>
        <button
          className={`nav-item ${currentTab === 'evidence' ? 'active' : ''}`}
          onClick={() => setCurrentTab('evidence')}
        >
          {t.navEvidence}
        </button>
        <button
          className={`nav-item ${currentTab === 'tests' ? 'active' : ''}`}
          onClick={() => setCurrentTab('tests')}
        >
          {t.navTests}
        </button>
      </nav>
    </header>
  );
};
