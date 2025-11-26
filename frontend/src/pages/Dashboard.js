import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Users, Megaphone, FileText, TrendingUp, Zap, Target } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const COLORS = ['#6366f1', '#3b82f6', '#8b5cf6', '#06b6d4'];

const Dashboard = ({ user, onLogout }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
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

  const statCards = [
    { icon: Users, label: 'Total Agents', value: stats?.agents_count || 0, color: 'from-indigo-500 to-blue-500', bgColor: 'bg-indigo-50' },
    { icon: Megaphone, label: 'Campaigns', value: stats?.campaigns_count || 0, color: 'from-blue-500 to-cyan-500', bgColor: 'bg-blue-50' },
    { icon: FileText, label: 'Documents', value: stats?.documents_count || 0, color: 'from-purple-500 to-pink-500', bgColor: 'bg-purple-50' },
    { icon: TrendingUp, label: 'Feedback', value: stats?.feedback_count || 0, color: 'from-green-500 to-emerald-500', bgColor: 'bg-green-50' },
  ];

  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="p-8" data-testid="dashboard-page">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Let’s build pipeline and close more  {user?.username}! 👋</h1>
          <p className="text-slate-600 text-lg">Here's what's happening with your sales operations today.</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {statCards.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div
                key={index}
                data-testid={`stat-card-${stat.label.toLowerCase().replace(/\s+/g, '-')}`}
                className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow duration-200 border border-slate-100"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className={`w-12 h-12 rounded-lg ${stat.bgColor} flex items-center justify-center`}>
                    <Icon className={`w-6 h-6 bg-gradient-to-br ${stat.color} bg-clip-text text-transparent`} />
                  </div>
                </div>
                <p className="text-3xl font-bold text-slate-900 mb-1">{stat.value}</p>
                <p className="text-sm text-slate-600 font-medium">{stat.label}</p>
              </div>
            );
          })}
        </div>

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-xl p-6 shadow-lg border border-slate-100">
            <h3 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
              <Zap className="text-indigo-600" size={24} />
              Recent Campaigns
            </h3>
            {stats?.recent_campaigns && stats.recent_campaigns.length > 0 ? (
              <div className="space-y-3">
                {stats.recent_campaigns.map((campaign, idx) => (
                  <div key={idx} className="p-4 bg-slate-50 rounded-lg border border-slate-200 hover:border-indigo-300 transition-colors">
                    <p className="font-semibold text-slate-900">{campaign.campaign_name}</p>
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-xs text-slate-600">{campaign.service} • {campaign.stage}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        campaign.status === 'published' ? 'bg-green-100 text-green-700' :
                        campaign.status === 'review' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-slate-100 text-slate-700'
                      }`}>
                        {campaign.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-500 text-center py-8">No campaigns yet. Create your first one!</p>
            )}
          </div>

          <div className="bg-white rounded-xl p-6 shadow-lg border border-slate-100">
            <h3 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
              <Target className="text-indigo-600" size={24} />
              Quick Actions
            </h3>
            <div className="space-y-3">
              <a
                href="/agents"
                data-testid="quick-action-agents"
                className="block p-4 bg-gradient-to-r from-indigo-50 to-blue-50 rounded-lg border border-indigo-200 hover:border-indigo-400 transition-colors"
              >
                <p className="font-semibold text-indigo-900">Create New Agent</p>
                <p className="text-sm text-indigo-700 mt-1">Build a new AI sales agent</p>
              </a>
              <a
                href="/campaigns"
                data-testid="quick-action-campaigns"
                className="block p-4 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg border border-blue-200 hover:border-blue-400 transition-colors"
              >
                <p className="font-semibold text-blue-900">Launch Campaign</p>
                <p className="text-sm text-blue-700 mt-1">Start a new outreach campaign</p>
              </a>
              <a
                href="/personalize"
                data-testid="quick-action-personalize"
                className="block p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-200 hover:border-purple-400 transition-colors"
              >
                <p className="font-semibold text-purple-900">Personalize Message</p>
                <p className="text-sm text-purple-700 mt-1">Generate 1:1 messages</p>
              </a>
            </div>
          </div>
        </div>

        {/* Performance Overview */}
        <div className="bg-white rounded-xl p-6 shadow-lg border border-slate-100">
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
      </div>
    </Layout>
  );
};

export default Dashboard;
