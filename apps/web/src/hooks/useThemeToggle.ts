import { useState, useEffect } from 'react';
import { getTimeTheme, getGradientIntensity, TimeTheme, ThemeConfig, themeConfigs } from './useTimeBasedTheme';

type ThemeMode = 'auto' | 'manual';

export const useThemeToggle = () => {
  const [themeMode, setThemeMode] = useState<ThemeMode>('auto');
  const [manualTheme, setManualTheme] = useState<TimeTheme>('noon');
  const [currentTheme, setCurrentTheme] = useState<TimeTheme>(getTimeTheme());
  const [intensity, setIntensity] = useState<number>(getGradientIntensity());
  
  // Initialize theme from localStorage
  useEffect(() => {
    const savedThemeMode = localStorage.getItem('themeMode') as ThemeMode || 'auto';
    const savedManualTheme = localStorage.getItem('manualTheme') as TimeTheme || 'noon';
    
    setThemeMode(savedThemeMode);
    setManualTheme(savedManualTheme);
    
    if (savedThemeMode === 'auto') {
      setCurrentTheme(getTimeTheme());
      setIntensity(getGradientIntensity());
    }
  }, []);
  
  // Update theme based on mode
  useEffect(() => {
    if (themeMode === 'auto') {
      const updateTheme = () => {
        setCurrentTheme(getTimeTheme());
        setIntensity(getGradientIntensity());
      };
      
      updateTheme();
      const interval = setInterval(updateTheme, 60000);
      return () => clearInterval(interval);
    } else {
      setCurrentTheme(manualTheme);
      setIntensity(1.0);
    }
  }, [themeMode, manualTheme]);
  
  const toggleThemeMode = () => {
    const newMode = themeMode === 'auto' ? 'manual' : 'auto';
    setThemeMode(newMode);
    localStorage.setItem('themeMode', newMode);
  };
  
  const setManualThemeAndSave = (theme: TimeTheme) => {
    setManualTheme(theme);
    localStorage.setItem('manualTheme', theme);
  };
  
  const getGradientStyle = () => {
    const themeConfig: ThemeConfig = themeConfigs[themeMode === 'auto' ? currentTheme : manualTheme];
    const currentIntensity = themeMode === 'auto' ? intensity : 1.0;
    
    return {
      background: `linear-gradient(135deg, ${themeConfig.gradientStart} 0%, ${themeConfig.gradientMiddle} 50%, ${themeConfig.gradientEnd} 100%)`,
      filter: `brightness(${currentIntensity})`,
    };
  };
  
  return {
    themeMode,
    currentTheme: themeMode === 'auto' ? currentTheme : manualTheme,
    manualTheme,
    intensity: themeMode === 'auto' ? intensity : 1.0,
    toggleThemeMode,
    setManualTheme: setManualThemeAndSave,
    getGradientStyle,
  };
};
