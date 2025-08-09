import React, { useState, useEffect, useRef } from 'react';
import Shell from '../components/layout/Shell';
import PageHeader from '../components/layout/PageHeader';

// Define types for our application
type AppType = 'general' | 'developer' | 'trader' | 'lawyer' | 'researcher' | 'data-engineer' | 'drawing' | 'terminal' | 'vm' | 'multi-model';

interface Message {
  id: string;
  content: string;
  type: 'user' | 'agent';
  timestamp: Date;
  app: AppType;
}

const Home: React.FC = () => {
  const [currentApp, setCurrentApp] = useState<AppType>('general');
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [toolsExpanded, setToolsExpanded] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Update placeholder based on current app
  const getPlaceholder = () => {
    const placeholders: Record<AppType, string> = {
      'general': 'Ask me anything...',
      'developer': 'Ask about coding and development...',
      'trader': 'Ask about trading and finance...',
      'lawyer': 'Ask about legal matters...',
      'researcher': 'Ask about research topics...',
      'data-engineer': 'Ask about data engineering...',
      'drawing': 'Let\'s create some art together...',
      'terminal': 'Execute terminal commands...',
      'vm': 'Manage containers and VMs...',
      'multi-model': 'Use advanced AI models...'
    };
    return placeholders[currentApp] || 'Message AGENT...';
  };

  // Handle sending a message
  const sendMessage = async () => {
    if (!inputValue.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      type: 'user',
      timestamp: new Date(),
      app: currentApp
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');

    try {
      // Send to backend
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: inputValue,
          domain: currentApp,
          app: currentApp
        })
      });

      const data = await response.json();

      if (data.success) {
        const agentMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: `🤖 **${currentApp.toUpperCase()} Response:**\n\n${data.result.answer}`,
          type: 'agent',
          timestamp: new Date(),
          app: currentApp
        };
        setMessages(prev => [...prev, agentMessage]);
      } else {
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: 'Sorry, I encountered an error: ' + data.error,
          type: 'agent',
          timestamp: new Date(),
          app: currentApp
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Network error: ' + (error instanceof Error ? error.message : 'Unknown error'),
        type: 'agent',
        timestamp: new Date(),
        app: currentApp
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  // Handle key press in input
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendMessage();
    }
  };

  // Toggle tools visibility
  const toggleTools = () => {
    setToolsExpanded(!toolsExpanded);
  };

  // Handle tool action
  const handleToolAction = (tool: string) => {
    const messages: Record<string, string> = {
      internet: "🌐 Internet search mode activated",
      upload: "📁 File upload ready",
      incognito: "🕵️ Incognito mode enabled",
      mpc: "🔗 Multi-party compute initialized"
    };

    const toolMessage: Message = {
      id: Date.now().toString(),
      content: messages[tool] || `${tool} tool activated`,
      type: 'agent',
      timestamp: new Date(),
      app: currentApp
    };

    setMessages(prev => [...prev, toolMessage]);
    setToolsExpanded(false);
  };

  // App selection
  const selectApp = (app: AppType) => {
    setCurrentApp(app);
  };

  return (
    <Shell title="Home">
      <div className="p-4 sm:p-6 lg:p-8">
        <PageHeader
          title="AGENT Interface"
          subtitle="Multi-domain AI assistant"
          breadcrumbs={[
            { label: 'Home' },
          ]}
        />
        
        {/* Messages area */}
        <div className="messages mb-4 p-4 bg-gray-100 rounded-lg h-96 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="welcome text-center py-8">
              <h2 className="text-2xl font-bold mb-2">Welcome to AGENT</h2>
              <p className="text-gray-600">Start a conversation by typing a message below</p>
            </div>
          ) : (
            messages.map((message) => (
              <div 
                key={message.id} 
                className={`message mb-4 p-3 rounded-lg ${
                  message.type === 'user' 
                    ? 'bg-blue-500 text-white self-end ml-auto max-w-xs' 
                    : 'bg-gray-200 text-gray-800 self-start mr-auto max-w-xs'
                }`}
              >
                <div className="message-content whitespace-pre-wrap">
                  {message.content}
                </div>
                <div className="message-meta text-xs mt-1 opacity-70">
                  {message.type === 'user' 
                    ? message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
                    : `AGENT • ${message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`}
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* App bar */}
        <div className="app-bar mb-4 flex overflow-x-auto pb-2">
          {(['general', 'developer', 'trader', 'lawyer', 'researcher', 'data-engineer', 'drawing', 'terminal', 'vm', 'multi-model'] as AppType[]).map((app) => (
            <button
              key={app}
              className={`app-item flex-shrink-0 px-3 py-2 rounded-full text-sm font-medium mr-2 ${
                currentApp === app
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
              onClick={() => selectApp(app)}
            >
              {app.charAt(0).toUpperCase() + app.slice(1)}
            </button>
          ))}
        </div>

        {/* Input area */}
        <div className="input-container bg-white rounded-lg p-4 shadow-md">
          {/* Tool buttons */}
          {toolsExpanded && (
            <div className="tool-buttons flex mb-2">
              <button 
                className="tool-btn p-2 bg-gray-200 rounded mr-2 hover:bg-gray-300"
                onClick={() => handleToolAction('internet')}
              >
                <i className="fas fa-globe"></i>
              </button>
              <button 
                className="tool-btn p-2 bg-gray-200 rounded mr-2 hover:bg-gray-300"
                onClick={() => handleToolAction('upload')}
              >
                <i className="fas fa-upload"></i>
              </button>
              <button 
                className="tool-btn p-2 bg-gray-200 rounded mr-2 hover:bg-gray-300"
                onClick={() => handleToolAction('incognito')}
              >
                <i className="fas fa-user-secret"></i>
              </button>
              <button 
                className="tool-btn p-2 bg-gray-200 rounded hover:bg-gray-300"
                onClick={() => handleToolAction('mpc')}
              >
                <i className="fas fa-network-wired"></i>
              </button>
            </div>
          )}

          {/* Input row */}
          <div className="input-row flex items-center">
            <button 
              className="plus-btn p-2 bg-blue-500 text-white rounded-full mr-2 hover:bg-blue-600"
              onClick={toggleTools}
            >
              <i className={`fas ${toolsExpanded ? 'fa-times' : 'fa-plus'}`}></i>
            </button>
            
            <input
              type="text"
              className="message-input flex-1 p-2 border border-gray-300 rounded mr-2"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={getPlaceholder()}
            />
            
            <button 
              className="send-btn p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              onClick={sendMessage}
            >
              <i className="fas fa-paper-plane"></i>
            </button>
          </div>
        </div>
      </div>
    </Shell>
  );
};

export default Home;