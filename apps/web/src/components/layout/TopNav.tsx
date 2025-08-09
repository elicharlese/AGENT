import React from 'react';
import { ArrowLeft, Menu } from 'lucide-react';

export type TopNavProps = {
  title?: string;
  leftSlot?: React.ReactNode;
  rightSlot?: React.ReactNode;
  showBackButton?: boolean;
  onBack?: () => void;
  mobileMenuOpen?: boolean;
  setMobileMenuOpen?: (open: boolean) => void;
};

export const TopNav: React.FC<TopNavProps> = ({ 
  title = 'App', 
  leftSlot, 
  rightSlot, 
  showBackButton = false, 
  onBack,
  mobileMenuOpen = false,
  setMobileMenuOpen
}) => {
  const handleBack = () => {
    if (onBack) {
      onBack();
    } else {
      window.history.back();
    }
  };

  const toggleMobileMenu = () => {
    if (setMobileMenuOpen) {
      setMobileMenuOpen(!mobileMenuOpen);
    }
  };
  
  return (
    <header className="sticky top-0 z-40 bg-white/80 backdrop-blur border-b border-default">
      <div className="mx-auto max-w-7xl px-m md:px-l lg:px-[calc(var(--space-l)*1.25)] h-14 flex items-center justify-between">
        <div className="flex items-center gap-s">
          {showBackButton && (
            <button
              onClick={handleBack}
              className="md:hidden flex items-center justify-center h-8 w-8 text-gray-600 hover:text-gray-900"
              aria-label="Go back"
            >
              <ArrowLeft size={20} />
            </button>
          )}
          <div className="h-8 w-8 bg-gray-900 text-white flex items-center justify-center radius-8 elev-sm">
            <span className="text-xs font-bold">UI</span>
          </div>
          {/* leftSlot if any */}
        </div>
        <nav className="hidden md:flex items-center gap-m text-sm text-gray-600">
          <a className="hover:text-gray-900" href="/dashboard">Dashboard</a>
          {/* more links */}
        </nav>
        <div className="flex items-center gap-s">
          {/* Mobile menu button */}
          <button
            className="md:hidden flex items-center justify-center h-8 w-8 text-gray-600 hover:text-gray-900"
            onClick={toggleMobileMenu}
            aria-label="Toggle menu"
          >
            <Menu size={20} />
          </button>
          {rightSlot}
        </div>
      </div>
    </header>
  );
};