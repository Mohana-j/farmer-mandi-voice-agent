import React, { useState } from 'react';
import { Language } from '../types';
import { translations } from '../i18n/translations';
import { speechSynthesizer } from '../services/speech';
import { Volume2, VolumeX, Calendar, ShieldCheck, AlertTriangle } from 'lucide-react';

interface VoiceAnswerProps {
  answerEn: string;
  answerTa: string;
  language: Language;
  observationDates: string[];
  sourceNames: string[];
  isYesterdayData: boolean;
  isStaleOrUncertain: boolean;
}

export const VoiceAnswer: React.FC<VoiceAnswerProps> = ({
  answerEn,
  answerTa,
  language,
  observationDates,
  sourceNames,
  isYesterdayData,
  isStaleOrUncertain,
}) => {
  const t = translations[language];
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [playbackLang, setPlaybackLang] = useState<Language>(language);

  const currentAnswerText = playbackLang === 'ta' ? answerTa : answerEn;

  const handleSpeak = () => {
    setIsSpeaking(true);
    speechSynthesizer.speak(currentAnswerText, playbackLang, () => {
      setIsSpeaking(false);
    });
  };

  const handleStop = () => {
    speechSynthesizer.stop();
    setIsSpeaking(false);
  };

  return (
    <div className="voice-answer-card">
      <div className="voice-answer-header">
        <div className="voice-title-group">
          <div className="voice-icon-box">
            <Volume2 size={24} color="#1b5e20" />
          </div>
          <div>
            <h3 className="voice-title">{t.voiceAnswerTitle}</h3>
            <span className="voice-subtitle">Grounded in verified observations</span>
          </div>
        </div>

        {/* Audio Language & Controls */}
        <div className="voice-audio-controls">
          <div className="voice-lang-tabs">
            <button
              className={`voice-tab-btn ${playbackLang === 'en' ? 'active' : ''}`}
              onClick={() => {
                handleStop();
                setPlaybackLang('en');
              }}
            >
              {t.voiceLanguageEn}
            </button>
            <button
              className={`voice-tab-btn ${playbackLang === 'ta' ? 'active' : ''}`}
              onClick={() => {
                handleStop();
                setPlaybackLang('ta');
              }}
            >
              {t.voiceLanguageTa}
            </button>
          </div>

          {!isSpeaking ? (
            <button className="btn-audio-speak" onClick={handleSpeak}>
              <Volume2 size={18} />
              <span>{t.btnSpeak}</span>
            </button>
          ) : (
            <button className="btn-audio-stop" onClick={handleStop}>
              <VolumeX size={18} />
              <span>{t.btnStopSpeak}</span>
            </button>
          )}
        </div>
      </div>

      {/* Spoken Transcript Bubble */}
      <div className="spoken-bubble">
        <p className="spoken-text">"{currentAnswerText}"</p>
      </div>

      {/* Uncertainty or Freshness Notice */}
      {(isYesterdayData || isStaleOrUncertain) && (
        <div className="notice-banner">
          <AlertTriangle size={18} color="#e65100" />
          <span>
            {isYesterdayData
              ? "Warning: Reported prices are from yesterday's market trading. Today's live market prices may fluctuate."
              : "Warning: Some records have unverified grades or units; comparison is marked provisional."}
          </span>
        </div>
      )}

      {/* Metadata Badges */}
      <div className="voice-meta-row">
        <div className="meta-badge">
          <Calendar size={14} />
          <span>Observation Dates: {observationDates.join(', ') || 'N/A'}</span>
        </div>
        <div className="meta-badge">
          <ShieldCheck size={14} />
          <span>Sources: {sourceNames.join(', ') || 'Agricultural Portals'}</span>
        </div>
      </div>
    </div>
  );
};
