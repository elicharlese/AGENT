import React, { useState } from 'react';
import { TopNav } from './TopNav';
import { SideNav } from './SideNav';

export type ShellProps = {
  title?: string;
  sidebar?: React.ReactNode; // allow custom sidebar or use built-in
  children: React.ReactNode;
  showBackButton?: boolean;
  onBack?: () => void;
};

export const Shell: React.FC<ShellProps> = ({ title, sidebar, children, showBackButton = false, onBack }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <TopNav 
        title={title} 
        showBackButton={showBackButton} 
        onBack={onBack}
        mobileMenuOpen={mobileMenuOpen}
        setMobileMenuOpen={setMobileMenuOpen}
      />
      <div className="flex">
        {/* Mobile sidebar overlay */}
        {mobileMenuOpen && (
          <div 
            className="fixed inset-0 z-40 lg:hidden" 
            onClick={() => setMobileMenuOpen(false)}
          >
            <div 
              className="fixed inset-y-0 left-0 z-50 w-64 border-r border-default bg-white"
              onClick={e => e.stopPropagation()}
            >
              {sidebar ?? <SideNav />}
            </div>
            <div className="fixed inset-0 bg-black bg-opacity-50"></div>
          </div>
        )}
        
        {/* Desktop sidebar */}
        <aside className="hidden lg:block w-64 border-r border-default bg-white">
          {sidebar ?? <SideNav />}
        </aside>

        {/* Content area */}
        <main className="flex-1 p-m md:p-l lg:p-[calc(var(--space-l)*1.25)]">{children}</main>
      </div>
    </div>
  );
};