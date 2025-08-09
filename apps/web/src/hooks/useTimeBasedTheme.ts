import { useState, useEffect } from 'react';

export type TimeTheme = 'dawn' | 'morning' | 'noon' | 'afternoon' | 'evening' | 'night' | 'midnight';

export interface ThemeConfig {
  gradientStart: string;
  gradientMiddle: string;
  gradientEnd: string;
  intensity: number;
  textColorPrimary: string;
  textColorSecondary: string;
}

export const themeConfigs: Record<TimeTheme, ThemeConfig> = {
  dawn: {
    gradientStart: '#ff7e5f',
    gradientMiddle: '#feb47b',
    gradientEnd: '#ff7e5f',
    intensity: 0.7,
    textColorPrimary: '#1f2937',
    textColorSecondary: '#6b7280',
  },
  morning: {
    gradientStart: '#667eea',
    gradientMiddle: '#764ba2',
    gradientEnd: '#667eea',
    intensity: 0.8,
    textColorPrimary: '#1f2937',
    textColorSecondary: '#6b7280',
  },
  noon: {
    gradientStart: '#f093fb',
    gradientMiddle: '#f5576c',
    gradientEnd: '#f093fb',
    intensity: 1.0,
    textColorPrimary: '#ffffff',
    textColorSecondary: '#f0f0f0',
  },
  afternoon: {
    gradientStart: '#43cea2',
    gradientMiddle: '#185a9d',
    gradientEnd: '#43cea2',
    intensity: 0.9,
    textColorPrimary: '#1f2937',
    textColorSecondary: '#6b7280',
  },
  evening: {
    gradientStart: '#834d9b',
    gradientMiddle: '#d04ed6',
    gradientEnd: '#834d9b',
    intensity: 0.85,
    textColorPrimary: '#ecf0f1',
    textColorSecondary: '#bdc3c7',
  },
  night: {
    gradientStart: '#2c3e50',
    gradientMiddle: '#34495e',
    gradientEnd: '#3c4c5c',
    intensity: 1.0,
    textColorPrimary: '#ecf0f1',
    textColorSecondary: '#bdc3c7',
  },
  midnight: {
    gradientStart: '#0f2027',
    gradientMiddle: '#203a43',
    gradientEnd: '#2c5364',
    intensity: 1.2,
    textColorPrimary: '#e0e0e0',
    textColorSecondary: '#a0a0a0',
  },
};

export const getTimeTheme = (): TimeTheme => {
  const hour = new Date().getHours();
  
  if (hour >= 5 && hour < 7) return 'dawn';
  if (hour >= 7 && hour < 10) return 'morning';
  if (hour >= 10 && hour < 12) return 'noon';
  if (hour >= 12 && hour < 16) return 'afternoon';
  if (hour >= 16 && hour < 19) return 'evening';
  if (hour >= 19 && hour < 23) return 'night';
  return 'midnight'; // 23:00 - 4:59
};

export const getGradientIntensity = (): number => {
  const hour = new Date().getHours();
  const minute = new Date().getMinutes();
  
  // Calculate smooth transition between themes
  if (hour >= 5 && hour < 7) { // Dawn transition
    if (hour === 5) return 0.5 + (minute / 60) * 0.2;
    if (hour === 6) return 0.7 + (minute / 60) * 0.1;
  } else if (hour >= 7 && hour < 10) { // Morning transition
    if (hour === 7) return 0.7 + (minute / 60) * 0.1;
    if (hour === 8) return 0.8 + (minute / 60) * 0.05;
    if (hour === 9) return 0.85 + (minute / 60) * 0.05;
  } else if (hour >= 10 && hour < 12) { // Noon transition
    if (hour === 10) return 0.9 + (minute / 60) * 0.05;
    if (hour === 11) return 0.95 + (minute / 60) * 0.05;
  } else if (hour >= 12 && hour < 16) { // Afternoon transition
    return 0.9 + (Math.sin((hour - 12) * Math.PI / 4) * 0.1);
  } else if (hour >= 16 && hour < 19) { // Evening transition
    if (hour === 16) return 0.95 - (minute / 60) * 0.1;
    if (hour === 17) return 0.85 - (minute / 60) * 0.1;
    if (hour === 18) return 0.75 - (minute / 60) * 0.1;
  } else if (hour >= 19 && hour < 23) { // Night transition
    if (hour === 19) return 0.75 - (minute / 60) * 0.1;
    if (hour >= 20 && hour < 23) return 0.65;
  } else { // Midnight transition
    return 1.0 + (Math.sin((hour - 23 + (minute / 60)) * Math.PI / 6) * 0.2);
  }
  
  return 1.0;
};

export const useTimeBasedTheme = () => {
  const [currentTheme, setCurrentTheme] = useState<TimeTheme>(getTimeTheme());
  const [intensity, setIntensity] = useState<number>(getGradientIntensity());
  
  useEffect(() => {
    const updateTheme = () => {
      setCurrentTheme(getTimeTheme());
      setIntensity(getGradientIntensity());
    };
    
    // Update theme immediately
    updateTheme();
    
    // Update theme every minute
    const interval = setInterval(updateTheme, 60000);
    
    return () => clearInterval(interval);
  }, []);
  
  const themeConfig = themeConfigs[currentTheme];
  
  return {
    currentTheme,
    intensity,
    themeConfig,
    getGradientStyle: () => ({
      background: `linear-gradient(135deg, ${themeConfig.gradientStart} 0%, ${themeConfig.gradientMiddle} 50%, ${themeConfig.gradientEnd} 100%)`,
      filter: `brightness(${intensity})`,
    }),
  };
};
