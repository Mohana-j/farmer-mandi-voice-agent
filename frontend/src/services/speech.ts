/**
 * Browser Web Speech API adapter for Speech-to-Text (STT) and Text-to-Speech (TTS).
 * Supports English (en-IN / en-US) and Tamil (ta-IN).
 */

export interface SpeechRecognitionAdapter {
  isSupported: boolean;
  start: (onResult: (text: string) => void, onError: (err: string) => void, onEnd: () => void, lang?: string) => void;
  stop: () => void;
}

// Window typing for Web Speech API
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

class BrowserSpeechRecognizer implements SpeechRecognitionAdapter {
  private recognition: any = null;
  public isSupported: boolean = false;

  constructor() {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.isSupported = !!SpeechRec;
    if (this.isSupported) {
      this.recognition = new SpeechRec();
      this.recognition.continuous = false;
      this.recognition.interimResults = true;
    }
  }

  start(
    onResult: (text: string) => void,
    onError: (err: string) => void,
    onEnd: () => void,
    lang: string = 'en'
  ) {
    if (!this.isSupported || !this.recognition) {
      onError('Speech recognition is not supported in this browser.');
      return;
    }

    this.recognition.lang = lang === 'ta' ? 'ta-IN' : 'en-IN';

    this.recognition.onresult = (event: any) => {
      let currentTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        currentTranscript += event.results[i][0].transcript;
      }
      onResult(currentTranscript);
    };

    this.recognition.onerror = (event: any) => {
      onError(event.error || 'Speech recognition encountered an error.');
    };

    this.recognition.onend = () => {
      onEnd();
    };

    try {
      this.recognition.start();
    } catch (e: any) {
      onError(e.message || 'Could not start microphone.');
    }
  }

  stop() {
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (e) {
        // Ignored
      }
    }
  }
}

class BrowserSpeechSynthesizer {
  public isSupported: boolean = typeof window !== 'undefined' && 'speechSynthesis' in window;

  speak(text: string, lang: string = 'en', onEnd?: () => void) {
    if (!this.isSupported) return;

    this.stop(); // Stop any active speech before starting new speech

    // Clean prefix like [Demo Mode] from speech if desired, or read it aloud
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang === 'ta' ? 'ta-IN' : 'en-IN';
    utterance.rate = 0.95; // Slightly slower for clarity in agricultural terms
    utterance.pitch = 1.0;

    // Attempt to pick optimal voice
    const voices = window.speechSynthesis.getVoices();
    const targetLangPrefix = lang === 'ta' ? 'ta' : 'en';
    const matchingVoice = voices.find((v) => v.lang.startsWith(targetLangPrefix));
    if (matchingVoice) {
      utterance.voice = matchingVoice;
    }

    if (onEnd) {
      utterance.onend = () => onEnd();
      utterance.onerror = () => onEnd();
    }

    window.speechSynthesis.speak(utterance);
  }

  stop() {
    if (this.isSupported) {
      window.speechSynthesis.cancel();
    }
  }
}

export const speechRecognizer = new BrowserSpeechRecognizer();
export const speechSynthesizer = new BrowserSpeechSynthesizer();
