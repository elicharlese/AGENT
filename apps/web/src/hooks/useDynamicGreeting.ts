import { useState, useEffect } from 'react';

export const useDynamicGreeting = () => {
  const [greeting, setGreeting] = useState('');
  
  const generateDynamicGreeting = () => {
    const now = new Date();
    const hour = now.getHours();
    const dayOfWeek = now.getDay();
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
    
    // Time-based greetings
    if (hour < 5) return "Good night, early riser";
    if (hour < 12) return "Good morning";
    if (hour < 18) return "Good afternoon";
    if (hour < 22) return "Good evening";
    return "Good night";
  };
  
  const getStatusMessage = () => {
    const statusMessages = [
      "AGENT - SYSTEMS ONLINE",
      "AGENT - READY FOR DEPLOYMENT",
      "AGENT - OPERATIONAL",
      "AGENT - AWAITING COMMAND",
      "AGENT - SYSTEMS NOMINAL",
      "AGENT - READY TO ASSIST",
      "AGENT - STATUS: GREEN",
      "AGENT - ALL SYSTEMS GO",
      "AGENT - ONLINE AND READY",
      "AGENT - FUNCTIONAL"
    ];
    
    return statusMessages[Math.floor(Math.random() * statusMessages.length)];
  };
  
  useEffect(() => {
    const updateGreeting = () => {
      const timeGreeting = generateDynamicGreeting();
      const statusMessage = getStatusMessage();
      setGreeting(`${timeGreeting} | ${statusMessage}`);
    };
    
    // Update greeting immediately
    updateGreeting();
    
    // Update greeting every minute
    const interval = setInterval(updateGreeting, 60000);
    
    return () => clearInterval(interval);
  }, []);
  
  return greeting;
};
