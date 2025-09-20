import { useEffect, useRef, useState } from 'react';

export function useSpeechRecorder() {
  const recognitionRef = useRef(null);
  const [isSupported, setIsSupported] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState(null);
  const [language, setLanguage] = useState('fr-FR');

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setIsSupported(false);
      setError("La reconnaissance vocale n'est pas supportée sur ce navigateur.");
      return;
    }
    setIsSupported(true);
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = language;

    recognition.onresult = (event) => {
      let finalTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const result = event.results[i];
        if (result.isFinal) {
          finalTranscript += `${result[0].transcript.trim()} `;
        }
      }
      if (finalTranscript) {
        setTranscript((prev) => `${prev} ${finalTranscript}`.trim());
      }
    };

    recognition.onerror = (event) => {
      setError(event.error);
      setIsRecording(false);
    };

    recognition.onend = () => {
      setIsRecording(false);
    };

    recognitionRef.current = recognition;
    return () => {
      recognition.stop();
    };
  }, [language]);

  const startRecording = () => {
    if (!isSupported || !recognitionRef.current) {
      return;
    }
    setError(null);
    recognitionRef.current.lang = language;
    recognitionRef.current.start();
    setIsRecording(true);
  };

  const stopRecording = () => {
    recognitionRef.current?.stop();
    setIsRecording(false);
  };

  const resetTranscript = () => {
    setTranscript('');
  };

  return {
    isSupported,
    isRecording,
    transcript,
    startRecording,
    stopRecording,
    resetTranscript,
    error,
    language,
    setLanguage
  };
}
