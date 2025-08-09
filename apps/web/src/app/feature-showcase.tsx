import React from 'react';
import { Shell } from '../components/layout/Shell';
import { ThemeToggleTest } from './test-components';
import { DynamicGreetingTest } from './test-components';
import { IMessageChatTest } from './test-components';

export default function FeatureShowcase() {
  return (
    <Shell title="Feature Showcase" showBackButton={true}>
      <div className="p-3 sm:p-4 md:p-6 lg:p-8 max-w-4xl mx-auto">
        <div className="mb-6 md:mb-8">
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">Feature Showcase</h1>
          <p className="text-sm md:text-base text-gray-600">Demonstration of implemented features from the static HTML app</p>
        </div>
        
        <div className="mb-6 md:mb-8">
          <h2 className="text-xl md:text-2xl font-semibold text-gray-800 mb-3 md:mb-4">Dynamic Greeting System</h2>
          <DynamicGreetingTest />
        </div>
        
        <div className="mb-6 md:mb-8">
          <h2 className="text-xl md:text-2xl font-semibold text-gray-800 mb-3 md:mb-4">Theme Toggle System</h2>
          <ThemeToggleTest />
        </div>
        
        <div className="mb-6 md:mb-8">
          <h2 className="text-xl md:text-2xl font-semibold text-gray-800 mb-3 md:mb-4">iMessage-Style Chat</h2>
          <div className="h-80 md:h-96">
            <IMessageChatTest />
          </div>
        </div>
      </div>
    </Shell>
  );
}
