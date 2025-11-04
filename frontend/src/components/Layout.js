import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Users, Megaphone, MessageSquare, Mail, FileText, Globe, TrendingUp, Bookmark, LogOut } from 'lucide-react';

const Layout = ({ children, user, onLogout }) => {
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/agents', icon: Users, label: 'Agent Builder' },
    { path: '/campaigns', icon: Megaphone, label: 'Campaigns' },
    { path: '/personalize', icon: MessageSquare, label: 'Personalize' },
    { path: '/thread-intelligence', icon: Mail, label: 'Thread Intelligence' },
    { path: '/documents', icon: FileText, label: 'Documents' },
    { path: '/gtm', icon: Globe, label: 'GTM Generator' },
    { path: '/learning', icon: TrendingUp, label: 'Learning Hub' },
    { path: '/saved', icon: Bookmark, label: 'Saved Items' },
  ];

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50" data-testid="layout-container">
      {/* Sidebar */}
      <aside className="w-64 bg-white/90 backdrop-blur-sm border-r border-slate-200 flex flex-col shadow-xl">
        <div className="p-6 border-b border-slate-200" data-testid="sidebar-header">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-blue-600 bg-clip-text text-transparent">
            SalesForce Pro
          </h1>
          <p className="text-sm text-slate-500 mt-1">AI-Powered Sales Platform</p>
        </div>

        <nav className="flex-1 p-4 overflow-y-auto" data-testid="sidebar-nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                data-testid={`nav-link-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-indigo-600 to-blue-600 text-white shadow-lg shadow-indigo-200'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                }`}
              >
                <Icon size={20} />
                <span className="font-medium text-sm">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-slate-200">
          <div className="flex items-center gap-3 mb-4 p-3 bg-slate-50 rounded-lg">
            <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-blue-500 rounded-full flex items-center justify-center text-white font-bold">
              {user?.username?.[0]?.toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-slate-900 truncate">{user?.username}</p>
              <p className="text-xs text-slate-500 truncate">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={onLogout}
            data-testid="logout-button"
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors duration-200 font-medium text-sm"
          >
            <LogOut size={16} />
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
};

export default Layout;
