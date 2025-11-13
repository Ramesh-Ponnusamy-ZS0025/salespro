import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';
import { Toaster } from 'sonner';

// Pages
import AuthPage from './pages/AuthPage';
import Dashboard from './pages/Dashboard';
import AgentBuilder from './pages/AgentBuilder';
import CampaignBuilder from './pages/CampaignBuilder';
import PersonalizationAssistant from './pages/PersonalizationAssistant';
import ThreadIntelligence from './pages/ThreadIntelligence';
import DocumentGenerator from './pages/DocumentGenerator';
import GTMGenerator from './pages/GTMGenerator';
import LearningHub from './pages/LearningHub';
import SavedItems from './pages/SavedItems';
import DocumentManagement from './pages/DocumentManagement';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Set axios defaults
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      try {
        const response = await axios.get(`${API}/auth/me`);
        setUser(response.data);
        setIsAuthenticated(true);
      } catch (error) {
        localStorage.removeItem('auth_token');
        setIsAuthenticated(false);
      }
    }
    setLoading(false);
  };

  const handleLogin = (token, userData) => {
    localStorage.setItem('auth_token', token);
    setUser(userData);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    setUser(null);
    setIsAuthenticated(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Toaster position="top-right" richColors />
      <Routes>
        <Route
          path="/auth"
          element={
            isAuthenticated ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <AuthPage onLogin={handleLogin} />
            )
          }
        />
        <Route
          path="/dashboard"
          element={
            isAuthenticated ? (
              <Dashboard user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/auth" replace />
            )
          }
        />
        <Route
          path="/agents"
          element={
            isAuthenticated ? (
              <AgentBuilder user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/auth" replace />
            )
          }
        />
        <Route
          path="/campaigns"
          element={
            isAuthenticated ? (
              <CampaignBuilder user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/auth" replace />
            )
          }
        />
        <Route
          path="/personalize"
          element={
            isAuthenticated ? (
              <PersonalizationAssistant user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/auth" replace />
            )
          }
        />
        <Route
          path="/thread-intelligence"
          element={
            isAuthenticated ? (
              <ThreadIntelligence user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/auth" replace />
            )
          }
        />
        <Route
          path="/documents"
          element={
            isAuthenticated ? (
              <DocumentGenerator user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/auth" replace />
            )
          }
        />
        <Route
          path="/gtm"
          element={
            isAuthenticated ? (
              <GTMGenerator user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/auth" replace />
            )
          }
        />
        <Route
          path="/learning"
          element={
            isAuthenticated ? (
              <LearningHub user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/auth" replace />
            )
          }
        />
        <Route
          path="/saved"
          element={
            isAuthenticated ? (
              <SavedItems user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/auth" replace />
            )
          }
        />
        <Route
          path="/document-management"
          element={
            isAuthenticated ? (
              <DocumentManagement user={user} onLogout={handleLogout} />
            ) : (
              <Navigate to="/auth" replace />
            )
          }
        />
        <Route
          path="/"
          element={<Navigate to={isAuthenticated ? "/dashboard" : "/auth"} replace />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
