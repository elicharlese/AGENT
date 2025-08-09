import React from 'react';
import IMessageChat from '../components/chat/IMessageChat';
import { useThemeToggle } from '../hooks/useThemeToggle';
import { useDynamicGreeting } from '../hooks/useDynamicGreeting';
import { useTimeBasedTheme } from '../hooks/useTimeBasedTheme';

// Test component for verifying the theme toggle hook
export const ThemeToggleTest: React.FC = () => {
  const { themeMode, currentTheme, manualTheme, intensity, toggleThemeMode, setManualTheme, getGradientStyle } = useThemeToggle();
  
  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h2>Theme Toggle Hook Test</h2>
      <div style={{ marginBottom: '10px' }}>
        <strong>Current Mode:</strong> {themeMode}
      </div>
      <div style={{ marginBottom: '10px' }}>
        <strong>Current Theme:</strong> {currentTheme}
      </div>
      <div style={{ marginBottom: '10px' }}>
        <strong>Intensity:</strong> {intensity.toFixed(2)}
      </div>
      <button 
        onClick={toggleThemeMode}
        style={{ padding: '8px 16px', marginRight: '10px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
      >
        Toggle Theme Mode
      </button>
      <button 
        onClick={() => setManualTheme('noon')}
        style={{ padding: '8px 16px', marginRight: '10px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
      >
        Set Manual Theme to Noon
      </button>
      <button 
        onClick={() => setManualTheme('night')}
        style={{ padding: '8px 16px', backgroundColor: '#6f42c1', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
      >
        Set Manual Theme to Night
      </button>
      <div style={{ marginTop: '20px', padding: '20px', ...getGradientStyle() }}>
        <h3>Gradient Preview</h3>
        <p>This div shows the current gradient style</p>
      </div>
    </div>
  );
};

// Test component for verifying the dynamic greeting hook
export const DynamicGreetingTest: React.FC = () => {
  const greeting = useDynamicGreeting();
  
  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h2>Dynamic Greeting Hook Test</h2>
      <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
        {greeting}
      </div>
    </div>
  );
};

// Test component for verifying the time-based theme hook
export const TimeBasedThemeTest: React.FC = () => {
  const { currentTheme, intensity, themeConfig, getGradientStyle } = useTimeBasedTheme();
  
  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h2>Time-Based Theme Hook Test</h2>
      <div style={{ marginBottom: '10px' }}>
        <strong>Current Theme:</strong> {currentTheme}
      </div>
      <div style={{ marginBottom: '10px' }}>
        <strong>Intensity:</strong> {intensity.toFixed(2)}
      </div>
      <div style={{ marginBottom: '10px' }}>
        <strong>Gradient Start:</strong> {themeConfig.gradientStart}
      </div>
      <div style={{ marginBottom: '10px' }}>
        <strong>Gradient Middle:</strong> {themeConfig.gradientMiddle}
      </div>
      <div style={{ marginBottom: '10px' }}>
        <strong>Gradient End:</strong> {themeConfig.gradientEnd}
      </div>
      <div style={{ marginTop: '20px', padding: '20px', ...getGradientStyle() }}>
        <h3>Gradient Preview</h3>
        <p>This div shows the current gradient style</p>
      </div>
    </div>
  );
};

// Test component for verifying the iMessage chat component
export const IMessageChatTest: React.FC = () => {
  return (
    <div style={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
      <IMessageChat />
    </div>
  );
};
