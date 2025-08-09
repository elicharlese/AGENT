import React, { useState, useEffect, useRef } from 'react';
import { useThemeToggle } from '../../hooks/useThemeToggle';
import { useDynamicGreeting } from '../../hooks/useDynamicGreeting';

interface Message {
  id: string;
  content: string;
  type: 'sent' | 'received';
  timestamp: Date;
}

const IMessageChat: React.FC = () => {
  const { getGradientStyle } = useThemeToggle();
  const dynamicGreeting = useDynamicGreeting();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Hello! How can I help you today?',
      type: 'received',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [currentApp, setCurrentApp] = useState('general');
  const [toolsExpanded, setToolsExpanded] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const apps = [
    { id: 'general', name: 'General', icon: '🤖' },
    { id: 'dev', name: 'Dev Tools', icon: '💻' },
    { id: 'design', name: 'Design', icon: '🎨' },
    { id: 'research', name: 'Research', icon: '🔍' },
    { id: 'writing', name: 'Writing', icon: '✍️' },
  ];

  const tools = [
    { id: 'internet', name: 'Internet Search', icon: '🌐' },
    { id: 'files', name: 'File Upload', icon: '📁' },
    { id: 'image', name: 'Image Generation', icon: '🖼️' },
    { id: 'code', name: 'Code Interpreter', icon: '⚡' },
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = () => {
    if (inputValue.trim() === '') return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      type: 'sent',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `I received your message about "${inputValue}". This is a simulated response from the ${currentApp} agent.`,
        type: 'received',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleToolAction = (toolId: string) => {
    console.log(`Tool action triggered: ${toolId}`);
    // In a real app, this would trigger the appropriate tool
  };

  return (
    <div className="flex flex-col h-full" style={getGradientStyle()}>
      {/* Header */}
      <div className="bg-gray-800/85 backdrop-blur-lg p-3 md:p-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">A</span>
            </div>
            <div className="min-w-0 flex-1">
              <h1 className="text-white font-semibold truncate">AGENT</h1>
              <p className="text-gray-300 text-xs truncate">{dynamicGreeting}</p>
            </div>
          </div>
          <div className="flex items-center gap-1 md:gap-2">
            <button className="p-1.5 md:p-2 rounded-full bg-gray-700 hover:bg-gray-600 transition">
              <svg className="w-4 h-4 md:w-5 md:h-5 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>
            <button className="p-1.5 md:p-2 rounded-full bg-gray-700 hover:bg-gray-600 transition">
              <svg className="w-4 h-4 md:w-5 md:h-5 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-3 md:p-4">
        <div className="max-w-4xl mx-auto space-y-3 md:space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'sent' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] md:max-w-xs lg:max-w-md xl:max-w-lg rounded-2xl px-3 py-2 md:px-4 md:py-2 ${message.type === 'sent'
                  ? 'bg-blue-500 text-white rounded-br-none md:rounded-br-none'
                  : 'bg-gray-700/50 text-white rounded-bl-none md:rounded-bl-none'
                  }`}
              >
                <p className="text-sm">{message.content}</p>
                <p className="text-xs opacity-70 mt-1">
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* App Switching Chips */}
      <div className="flex overflow-x-auto gap-2 p-3 md:p-4 border-b border-gray-700 bg-gray-800/50">
        {apps.map((app) => (
          <button
            key={app.id}
            className={`flex-shrink-0 px-2.5 py-1 md:px-3 md:py-1.5 rounded-full text-xs font-medium transition ${app.id === currentApp ? 'bg-blue-500 text-white' : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600'}`}
            onClick={() => setCurrentApp(app.id)}
          >
            <span className="mr-1">{app.icon}</span>
            <span className="whitespace-nowrap">{app.name}</span>
          </button>
        ))}
      </div>

      {/* Input Area */}
      <div className="p-3 md:p-4 border-t border-gray-700 bg-gray-800/50">
        {/* Expandable Tools */}
        {toolsExpanded && (
          <div className="mb-3 flex overflow-x-auto gap-2 pb-2">
            {tools.map((tool) => (
              <button
                key={tool.id}
                className="flex-shrink-0 flex flex-col items-center justify-center p-2 rounded-lg bg-gray-700/50 hover:bg-gray-600 transition min-w-[50px] md:min-w-[60px]"
                onClick={() => {
                  // Handle tool selection
                  console.log(`Selected tool: ${tool.id}`);
                }}
              >
                <span className="text-lg mb-1">{tool.icon}</span>
                <span className="text-xs text-gray-300">{tool.name}</span>
              </button>
            ))}
          </div>
        )}

        {/* Input and Send */}
        <div className="flex gap-2">
          <button
            className="p-2 rounded-full bg-gray-700 hover:bg-gray-600 transition"
            onClick={() => setToolsExpanded(!toolsExpanded)}
          >
            <svg className="w-5 h-5 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </button>
          <div className="flex-1 relative">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Message AGENT..."
              className="w-full bg-gray-700/50 text-white rounded-2xl py-2.5 md:py-3 px-3 md:px-4 pr-10 md:pr-12 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 max-h-32"
              rows={1}
            />
            <button
              onClick={handleSendMessage}
              disabled={inputValue.trim() === ''}
              className="absolute right-1.5 md:right-2 bottom-1.5 md:bottom-2 p-1 rounded-full bg-blue-500 hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              <svg className="w-4 h-4 md:w-5 md:h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IMessageChat;
