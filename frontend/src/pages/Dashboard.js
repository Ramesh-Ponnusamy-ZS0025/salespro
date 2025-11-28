import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { Calendar, Newspaper, Trophy, Globe, ChevronDown, ChevronUp } from 'lucide-react';
import { Card } from '../components/ui/card';
import { Label } from '../components/ui/label';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = ({ user, onLogout }) => {
  const [stats, setStats] = useState(null);
  const [zuciNews, setZuciNews] = useState([]);
  const [zuciWins, setZuciWins] = useState([]);
  const [gtmEntries, setGtmEntries] = useState([]);
  const [loading, setLoading] = useState(true);

  // Expanded states for each panel
  const [expandedNewsId, setExpandedNewsId] = useState(null);
  const [expandedWinId, setExpandedWinId] = useState(null);
  const [expandedGtmId, setExpandedGtmId] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch dashboard stats
      const statsResponse = await axios.get(`${API}/dashboard/stats`);
      setStats(statsResponse.data);

      // Fetch Zuci News (sorted by published_date desc)
      const newsResponse = await axios.get(`${API}/zuci-news`);
      setZuciNews(newsResponse.data.slice(0, 5)); // Top 5

      // Fetch Zuci Wins (sorted by win_date desc)
      const winsResponse = await axios.get(`${API}/zuci-wins`);
      setZuciWins(winsResponse.data.slice(0, 5)); // Top 5

      // Fetch GTM Entries
      const gtmResponse = await axios.get(`${API}/gtm-entries`);
      setGtmEntries(gtmResponse.data.slice(0, 5)); // Top 5
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatDateLong = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <Layout user={user} onLogout={onLogout}>
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="p-8" data-testid="dashboard-page">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">
            Let's build pipeline and close more {user?.username}! 👋
          </h1>
          <p className="text-slate-600 text-lg">Here's what's happening with your sales operations today.</p>
        </div>

        {/* Platform Overview */}
        <div className="bg-white rounded-xl p-6 shadow-lg border border-slate-100 mb-8">
          <h3 className="text-xl font-bold text-slate-900 mb-6">Platform Overview</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-4 bg-gradient-to-br from-indigo-50 to-blue-50 rounded-lg border border-indigo-100">
              <p className="text-sm text-indigo-700 font-medium mb-2">Total Agents</p>
              <p className="text-3xl font-bold text-indigo-900">{stats?.agents_count || 0}</p>
              <p className="text-xs text-indigo-600 mt-2">AI-powered sales agents</p>
            </div>
            <div className="p-4 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg border border-blue-100">
              <p className="text-sm text-blue-700 font-medium mb-2">Active Campaigns</p>
              <p className="text-3xl font-bold text-blue-900">{stats?.campaigns_count || 0}</p>
              <p className="text-xs text-blue-600 mt-2">Multi-touch campaigns</p>
            </div>
            <div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg border border-purple-100">
              <p className="text-sm text-purple-700 font-medium mb-2">Generated Docs</p>
              <p className="text-3xl font-bold text-purple-900">{stats?.documents_count || 0}</p>
              <p className="text-xs text-purple-600 mt-2">NDAs, MSAs, SOWs</p>
            </div>
          </div>
        </div>

        {/* Content Management Panels */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Zuci News Panel */}
          <div className="bg-white rounded-xl p-6 shadow-lg border border-slate-100">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-blue-500 rounded-lg flex items-center justify-center">
                <Newspaper className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-bold text-slate-900">Zuci News</h3>
            </div>
            {zuciNews.length === 0 ? (
              <p className="text-slate-500 text-sm text-center py-8">No news articles yet</p>
            ) : (
              <div className="space-y-3">
                {zuciNews.map((news) => (
                  <Card key={news.id} className="overflow-hidden hover:shadow-md transition-shadow">
                    <div
                      onClick={() => setExpandedNewsId(expandedNewsId === news.id ? null : news.id)}
                      className="p-3 cursor-pointer hover:bg-slate-50 transition-colors flex items-center justify-between"
                    >
                      <div className="flex-1">
                        <h4 className="font-semibold text-slate-900 text-sm mb-1 line-clamp-2">
                          {news.title}
                        </h4>
                        <div className="flex items-center text-xs text-slate-600">
                          <Calendar size={12} className="mr-1" />
                          {formatDate(news.published_date)}
                        </div>
                      </div>
                      <div className="ml-2 text-slate-400">
                        {expandedNewsId === news.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                      </div>
                    </div>

                    {expandedNewsId === news.id && (
                      <div className="border-t border-slate-200 bg-slate-50 p-3">
                        <div className="mb-3">
                          <Label className="text-xs font-semibold text-slate-700 mb-1 block">Published</Label>
                          <p className="text-xs text-slate-600">{formatDateLong(news.published_date)}</p>
                        </div>
                        <div className="mb-3">
                          <Label className="text-xs font-semibold text-slate-700 mb-1 block">Description</Label>
                          <p className="text-xs text-slate-800 whitespace-pre-wrap">{news.description}</p>
                        </div>
                        {news.news_link && (
                          <div>
                            <Label className="text-xs font-semibold text-slate-700 mb-1 block">News Link</Label>
                            <a
                              href={news.news_link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-indigo-600 hover:text-indigo-800 underline break-all"
                              onClick={(e) => e.stopPropagation()}
                            >
                              {news.news_link}
                            </a>
                          </div>
                        )}
                      </div>
                    )}
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* Zuci Wins Panel */}
          <div className="bg-white rounded-xl p-6 shadow-lg border border-slate-100">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-500 rounded-lg flex items-center justify-center">
                <Trophy className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-bold text-slate-900">Zuci Wins</h3>
            </div>
            {zuciWins.length === 0 ? (
              <p className="text-slate-500 text-sm text-center py-8">No wins yet</p>
            ) : (
              <div className="space-y-3">
                {zuciWins.map((win) => (
                  <Card key={win.id} className="overflow-hidden hover:shadow-md transition-shadow">
                    <div
                      onClick={() => setExpandedWinId(expandedWinId === win.id ? null : win.id)}
                      className="p-3 cursor-pointer hover:bg-slate-50 transition-colors flex items-center justify-between"
                    >
                      <div className="flex-1">
                        <h4 className="font-semibold text-slate-900 text-sm mb-1">
                          {win.company_name}
                        </h4>
                        <div className="flex items-center text-xs text-slate-600">
                          <Calendar size={12} className="mr-1" />
                          {formatDate(win.win_date)}
                        </div>
                      </div>
                      <div className="ml-2 text-slate-400">
                        {expandedWinId === win.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                      </div>
                    </div>

                    {expandedWinId === win.id && (
                      <div className="border-t border-slate-200 bg-slate-50 p-3">
                        <div className="mb-3">
                          <Label className="text-xs font-semibold text-slate-700 mb-1 block">Win Date</Label>
                          <p className="text-xs text-slate-600">{formatDateLong(win.win_date)}</p>
                        </div>
                        <div className="mb-3">
                          <Label className="text-xs font-semibold text-slate-700 mb-1 block">Description</Label>
                          <p className="text-xs text-slate-800 whitespace-pre-wrap">{win.description}</p>
                        </div>
                        {win.contributions && win.contributions.length > 0 && (
                          <div>
                            <Label className="text-xs font-semibold text-slate-700 mb-1 block">Contributors</Label>
                            <div className="space-y-2">
                              {win.contributions.map((contrib, idx) => (
                                <div key={idx} className="p-2 bg-white rounded border border-slate-200">
                                  <p className="font-medium text-slate-900 text-xs">{contrib.name}</p>
                                  <p className="text-xs text-slate-600">{contrib.designation}</p>
                                  <p className="text-xs text-slate-500">{contrib.email}</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* GTM Panel */}
          <div className="bg-white rounded-xl p-6 shadow-lg border border-slate-100">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <Globe className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-bold text-slate-900">GTM</h3>
            </div>
            {gtmEntries.length === 0 ? (
              <p className="text-slate-500 text-sm text-center py-8">No GTM entries yet</p>
            ) : (
              <div className="space-y-3">
                {gtmEntries.map((gtm) => (
                  <Card key={gtm.id} className="overflow-hidden hover:shadow-md transition-shadow">
                    <div
                      onClick={() => setExpandedGtmId(expandedGtmId === gtm.id ? null : gtm.id)}
                      className="p-3 cursor-pointer hover:bg-slate-50 transition-colors flex items-center justify-between"
                    >
                      <div className="flex-1">
                        <h4 className="font-semibold text-indigo-600 text-sm mb-1">
                          {gtm.prospect_name}
                        </h4>
                        <div className="flex items-center text-xs text-slate-600">
                          <Calendar size={12} className="mr-1" />
                          {formatDate(gtm.date)}
                        </div>
                      </div>
                      <div className="ml-2 text-slate-400">
                        {expandedGtmId === gtm.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                      </div>
                    </div>

                    {expandedGtmId === gtm.id && (
                      <div className="border-t border-slate-200 bg-slate-50 p-3">
                        <div className="mb-3">
                          <Label className="text-xs font-semibold text-slate-700 mb-1 block">Date</Label>
                          <p className="text-xs text-slate-600">{formatDateLong(gtm.date)}</p>
                        </div>
                        <div className="mb-3">
                          <Label className="text-xs font-semibold text-slate-700 mb-1 block">Description</Label>
                          <p className="text-xs text-slate-800 whitespace-pre-wrap">{gtm.description}</p>
                        </div>
                        <div>
                          <Label className="text-xs font-semibold text-slate-700 mb-1 block">GTM Link</Label>
                          <a
                            href={gtm.gtm_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-indigo-600 hover:text-indigo-800 underline break-all"
                            onClick={(e) => e.stopPropagation()}
                          >
                            {gtm.gtm_link}
                          </a>
                        </div>
                      </div>
                    )}
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
