/**
 * GrowthGuru AI — Layout Component
 * ==================================
 * Shared app shell with fixed sidebar and top navigation.
 * Per UI/UX spec §5: Sidebar 250px, Top Nav 64px.
 * Mobile: sidebar hidden, hamburger toggle.
 */

import { useState } from 'react';
import {
  Home,
  Upload,
  BarChart3,
  Sparkles,
  Menu,
  X,
} from 'lucide-react';

const NAV_ITEMS = [
  { id: 'home', label: 'Home', icon: Home },
  { id: 'upload', label: 'Upload CSV', icon: Upload },
  { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
  { id: 'coach', label: 'GrowthEngine™', icon: Sparkles },
];

const PAGE_TITLES = {
  home: 'Business Profile',
  upload: 'Upload Sales Data',
  dashboard: 'Dashboard Analytics',
  coach: 'GrowthEngine™',
};

export default function Layout({ currentScreen, setCurrentScreen, children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleNavClick = (screenId) => {
    setCurrentScreen(screenId);
    setSidebarOpen(false);
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed lg:static inset-y-0 left-0 z-30
          w-sidebar bg-sidebar border-r border-border
          flex flex-col
          transform transition-transform duration-200 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
        role="navigation"
        aria-label="Main navigation"
      >
        {/* Logo area */}
        <div className="h-topnav flex items-center px-md border-b border-border">
          <div className="flex items-center gap-xs">
            <Sparkles className="w-6 h-6 text-primary" />
            <span className="text-lg font-semibold text-text-main">
              GrowthGuru <span className="text-primary">AI</span>
            </span>
          </div>
          {/* Mobile close button */}
          <button
            className="ml-auto lg:hidden text-text-muted hover:text-text-main transition-colors"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close sidebar"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation items */}
        <nav className="flex-1 py-sm">
          <ul className="space-y-xxs">
            {NAV_ITEMS.map(({ id, label, icon: Icon }) => {
              const isActive = currentScreen === id;
              return (
                <li key={id}>
                  <button
                    onClick={() => handleNavClick(id)}
                    className={`
                      w-full flex items-center gap-xs px-md py-xs text-body
                      transition-colors duration-150
                      border-l-[3px]
                      ${isActive
                        ? 'border-primary text-primary bg-primary/5'
                        : 'border-transparent text-text-muted hover:text-text-main hover:bg-white/[0.02]'
                      }
                    `}
                    aria-current={isActive ? 'page' : undefined}
                  >
                    <Icon className="w-[18px] h-[18px] flex-shrink-0" />
                    <span>{label}</span>
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Footer */}
        <div className="p-md border-t border-border">
          <p className="text-small text-text-muted">
            Hackathon PoC v1.0
          </p>
        </div>
      </aside>

      {/* Main content area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Navigation */}
        <header className="h-topnav bg-bg border-b border-border flex items-center px-md flex-shrink-0">
          {/* Mobile hamburger */}
          <button
            className="lg:hidden mr-sm text-text-muted hover:text-text-main transition-colors"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open sidebar"
          >
            <Menu className="w-5 h-5" />
          </button>

          <h1 className="text-h1 text-text-main truncate">
            {PAGE_TITLES[currentScreen] || 'GrowthGuru AI'}
          </h1>
        </header>

        {/* Scrollable content */}
        <main className="flex-1 overflow-y-auto p-md bg-bg">
          <div className="max-w-6xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
