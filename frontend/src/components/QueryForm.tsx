import React, { useState } from 'react';
import { Language } from '../types';
import { translations } from '../i18n/translations';
import { speechRecognizer } from '../services/speech';
import { Mic, MicOff, Search, AlertCircle, RefreshCw, Sparkles } from 'lucide-react';

interface QueryFormProps {
  language: Language;
  onSubmitQuery: (data: {
    crop: string;
    grade: string;
    location: string;
    radius_km: number;
    language: Language;
    transcript?: string;
  }) => Promise<void>;
  isSearching: boolean;
  activeQueryId?: string | null;
}

export const QueryForm: React.FC<QueryFormProps> = ({
  language,
  onSubmitQuery,
  isSearching,
  activeQueryId,
}) => {
  const t = translations[language];

  const [crop, setCrop] = useState('tomato');
  const [grade, setGrade] = useState('Grade A');
  const [location, setLocation] = useState('Dharmapuri');
  const [radiusKm, setRadiusKm] = useState(50);
  const [transcript, setTranscript] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState<string | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);

  // Quick crop chips
  const quickCrops = [
    { label: 'Tomato / தக்காளி', value: 'tomato' },
    { label: 'Onion / வெங்காயம்', value: 'onion' },
    { label: 'Potato / உருளைக்கிழங்கு', value: 'potato' },
    { label: 'Chilli / மிளகாய்', value: 'chilli' },
    { label: 'Brinjal / கத்தரிக்காய்', value: 'brinjal' },
  ];

  const handleStartRecording = () => {
    if (!speechRecognizer.isSupported) {
      setVoiceStatus(t.micNotSupported);
      return;
    }

    setValidationError(null);
    setIsRecording(true);
    setVoiceStatus(t.micListening);

    speechRecognizer.start(
      (text: string) => {
        setTranscript(text);
        // Simple client-side auto-fill if keywords match
        const lower = text.toLowerCase();
        if (lower.includes('தக்காளி') || lower.includes('tomato')) setCrop('tomato');
        if (lower.includes('வெங்காயம்') || lower.includes('onion')) setCrop('onion');
        if (lower.includes('பாலக்கோடு') || lower.includes('palacode')) setLocation('Palacode');
        if (lower.includes('கிருஷ்ணகிரி') || lower.includes('krishnagiri')) setLocation('Krishnagiri');
      },
      (error: string) => {
        setIsRecording(false);
        setVoiceStatus(`${t.micPermissionDenied} (${error})`);
      },
      () => {
        setIsRecording(false);
        setVoiceStatus(null);
      },
      language
    );
  };

  const handleStopRecording = () => {
    speechRecognizer.stop();
    setIsRecording(false);
    setVoiceStatus(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    // Strict validation: do not silently guess missing parameters
    if (!crop || !crop.trim()) {
      setValidationError('Please select or specify a crop.');
      return;
    }
    if (!location || !location.trim()) {
      setValidationError('Please enter a valid reference town, village or market location.');
      return;
    }
    if (radiusKm <= 0 || radiusKm > 500) {
      setValidationError('Search radius must be between 1 and 500 km.');
      return;
    }

    await onSubmitQuery({
      crop: crop.trim(),
      grade: grade.trim(),
      location: location.trim(),
      radius_km: radiusKm,
      language,
      transcript: transcript.trim() || undefined,
    });
  };

  return (
    <div className="query-form-card panel">
      <div className="panel-header">
        <div>
          <h2 className="panel-title">{t.formTitle}</h2>
          <p className="panel-subtitle">{t.formSubtitle}</p>
        </div>
        {activeQueryId && (
          <span className="query-id-tag">Active Query: {activeQueryId}</span>
        )}
      </div>

      {/* Voice Dictation Section */}
      <div className="voice-input-banner">
        <div className="voice-controls-row">
          <div className="voice-label-group">
            <span className="voice-section-title">{t.labelMic}</span>
            <span className="voice-hint">Supports English and Tamil speech recognition</span>
          </div>
          <div>
            {!isRecording ? (
              <button
                type="button"
                className="btn-mic-start"
                onClick={handleStartRecording}
                disabled={isSearching}
              >
                <Mic size={18} />
                <span>{t.btnStartRecord}</span>
              </button>
            ) : (
              <button
                type="button"
                className="btn-mic-stop"
                onClick={handleStopRecording}
              >
                <MicOff size={18} />
                <span>{t.btnStopRecord}</span>
              </button>
            )}
          </div>
        </div>

        {voiceStatus && (
          <div className={`voice-status-box ${isRecording ? 'recording' : 'error'}`}>
            {isRecording && <span className="voice-pulse-indicator"></span>}
            <span>{voiceStatus}</span>
          </div>
        )}

        {/* Editable Transcript */}
        <div className="form-field-group transcript-field-group">
          <label className="field-label">{t.labelTranscript}</label>
          <textarea
            className="input-transcript"
            rows={2}
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            placeholder={t.placeholderTranscript}
          />
          <span className="field-help-text">
            You can freely edit or type in this box before clicking search.
          </span>
        </div>
      </div>

      {/* Query Parameters Form */}
      <form onSubmit={handleSubmit} className="query-fields-grid">
        {/* Quick Crop Selector */}
        <div className="form-field full-width">
          <label className="field-label">{t.labelCrop}</label>
          <div className="chips-row">
            {quickCrops.map((c) => (
              <button
                key={c.value}
                type="button"
                className={`chip-btn ${crop.toLowerCase() === c.value ? 'selected' : ''}`}
                onClick={() => setCrop(c.value)}
              >
                {c.label}
              </button>
            ))}
          </div>
          <input
            type="text"
            className="input-text"
            value={crop}
            onChange={(e) => setCrop(e.target.value)}
            placeholder="Or type custom crop..."
          />
        </div>

        {/* Grade */}
        <div className="form-field">
          <label className="field-label">{t.labelGrade}</label>
          <select
            className="input-select"
            value={grade}
            onChange={(e) => setGrade(e.target.value)}
          >
            <option value="Grade A">{t.gradeOptionA}</option>
            <option value="Grade B">{t.gradeOptionB}</option>
            <option value="Grade C">{t.gradeOptionC}</option>
            <option value="FAQ">{t.gradeOptionFaq}</option>
            <option value="unknown">{t.gradeOptionUnknown}</option>
          </select>
        </div>

        {/* Location */}
        <div className="form-field">
          <label className="field-label">{t.labelLocation}</label>
          <input
            type="text"
            className="input-text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="e.g. Dharmapuri, Palacode, Salem"
          />
        </div>

        {/* Radius */}
        <div className="form-field">
          <div className="radius-label-row">
            <label className="field-label">{t.labelRadius}</label>
            <span className="radius-value-pill">{radiusKm} km</span>
          </div>
          <input
            type="range"
            min="5"
            max="150"
            step="5"
            className="input-range"
            value={radiusKm}
            onChange={(e) => setRadiusKm(Number(e.target.value))}
          />
        </div>

        {/* Validation Alert */}
        {validationError && (
          <div className="validation-alert full-width">
            <AlertCircle size={18} />
            <span>{validationError}</span>
          </div>
        )}

        {/* Submit Button */}
        <div className="form-submit-row full-width">
          <button
            type="submit"
            className="btn-submit-search"
            disabled={isSearching}
          >
            {isSearching ? (
              <>
                <RefreshCw size={20} className="spin" />
                <span>{t.searching}</span>
              </>
            ) : (
              <>
                <Search size={20} />
                <span>{t.btnSearch}</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
