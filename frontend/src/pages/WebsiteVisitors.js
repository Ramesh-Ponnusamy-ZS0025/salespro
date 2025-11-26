import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { Card } from '../components/ui/card';
import { 
  Users, 
  TrendingUp, 
  Globe, 
  Clock, 
  MapPin, 
  Building2,
  Eye,
  MousePointer,
  Filter,
  Download,
  RefreshCw
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';

// Mock data for website visitors (simulating ZoomInfo data)
const MOCK_VISITORS = [
  {
    id: 1,
    company: "Acme Corporation",
    industry: "Technology",
    location: "San Francisco, CA",
    employees: "1000-5000",
    revenue: "$100M-$500M",
    visitDate: "2024-11-24T14:30:00",
    pageViews: 12,
    duration: "8m 45s",
    pages: ["Homepage", "Product", "Pricing", "Case Studies"],
    ipAddress: "192.168.1.1",
    intent: "High",
    status: "New"
  },
  {
    id: 2,
    company: "Global Innovations Inc",
    industry: "Financial Services",
    location: "New York, NY",
    employees: "5000+",
    revenue: "$1B+",
    visitDate: "2024-11-24T13:15:00",
    pageViews: 8,
    duration: "6m 20s",
    pages: ["Homepage", "Solutions", "Contact"],
    ipAddress: "192.168.1.2",
    intent: "Medium",
    status: "Returning"
  },
  {
    id: 3,
    company: "TechStart Solutions",
    industry: "Software",
    location: "Austin, TX",
    employees: "100-500",
    revenue: "$10M-$50M",
    visitDate: "2024-11-24T12:45:00",
    pageViews: 15,
    duration: "12m 30s",
    pages: ["Homepage", "Product", "Demo", "Pricing", "Contact"],
    ipAddress: "192.168.1.3",
    intent: "High",
    status: "Returning"
  },
  {
    id: 4,
    company: "Healthcare Partners LLC",
    industry: "Healthcare",
    location: "Boston, MA",
    employees: "500-1000",
    revenue: "$50M-$100M",
    visitDate: "2024-11-24T11:20:00",
    pageViews: 5,
    duration: "3m 15s",
    pages: ["Homepage", "About"],
    ipAddress: "192.168.1.4",
    intent: "Low",
    status: "New"
  },
  {
    id: 5,
    company: "Retail Dynamics Corp",
    industry: "Retail",
    location: "Chicago, IL",
    employees: "1000-5000",
    revenue: "$500M-$1B",
    visitDate: "2024-11-24T10:50:00",
    pageViews: 10,
    duration: "7m 45s",
    pages: ["Homepage", "Solutions", "Case Studies", "Pricing"],
    ipAddress: "192.168.1.5",
    intent: "High",
    status: "New"
  },
  {
    id: 6,
    company: "Manufacturing Excellence",
    industry: "Manufacturing",
    location: "Detroit, MI",
    employees: "5000+",
    revenue: "$1B+",
    visitDate: "2024-11-24T10:10:00",
    pageViews: 6,
    duration: "4m 30s",
    pages: ["Homepage", "Product", "Resources"],
    ipAddress: "192.168.1.6",
    intent: "Medium",
    status: "Returning"
  },
  {
    id: 7,
    company: "EduTech Innovations",
    industry: "Education",
    location: "Seattle, WA",
    employees: "100-500",
    revenue: "$10M-$50M",
    visitDate: "2024-11-23T16:30:00",
    pageViews: 9,
    duration: "6m 15s",
    pages: ["Homepage", "Solutions", "Demo", "Blog"],
    ipAddress: "192.168.1.7",
    intent: "Medium",
    status: "New"
  },
  {
    id: 8,
    company: "CloudScale Systems",
    industry: "Cloud Services",
    location: "San Jose, CA",
    employees: "500-1000",
    revenue: "$100M-$500M",
    visitDate: "2024-11-23T15:45:00",
    pageViews: 18,
    duration: "15m 20s",
    pages: ["Homepage", "Product", "Pricing", "Case Studies", "Contact", "Demo"],
    ipAddress: "192.168.1.8",
    intent: "High",
    status: "Returning"
  }
];

const MOCK_STATS = {
  totalVisitors: 156,
  highIntent: 42,
  newCompanies: 89,
  returningCompanies: 67
};

const WebsiteVisitors = ({ user, onLogout }) => {
  const [visitors, setVisitors] = useState([]);
  const [stats, setStats] = useState(MOCK_STATS);
  const [loading, setLoading] = useState(true);
  const [selectedIntent, setSelectedIntent] = useState('All');
  const [selectedIndustry, setSelectedIndustry] = useState('All');

  useEffect(() => {
    // Simulate data loading
    setTimeout(() => {
      setVisitors(MOCK_VISITORS);
      setLoading(false);
    }, 1000);
  }, []);

  const getIntentBadge = (intent) => {
    const variants = {
      'High': 'bg-red-100 text-red-700 border-red-300',
      'Medium': 'bg-yellow-100 text-yellow-700 border-yellow-300',
      'Low': 'bg-gray-100 text-gray-700 border-gray-300'
    };
    return variants[intent] || variants['Low'];
  };

  const getStatusBadge = (status) => {
    return status === 'New' 
      ? 'bg-green-100 text-green-700 border-green-300'
      : 'bg-blue-100 text-blue-700 border-blue-300';
  };

  const filteredVisitors = visitors.filter(visitor => {
    if (selectedIntent !== 'All' && visitor.intent !== selectedIntent) return false;
    if (selectedIndustry !== 'All' && visitor.industry !== selectedIndustry) return false;
    return true;
  });

  const industries = ['All', ...new Set(visitors.map(v => v.industry))];

  const formatDateTime = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-slate-900 mb-2">Website Visitors</h1>
            <p className="text-slate-600">Track and analyze companies visiting your website</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setLoading(true)}>
              <RefreshCw size={16} className="mr-2" />
              Refresh
            </Button>
            <Button variant="outline">
              <Download size={16} className="mr-2" />
              Export
            </Button>
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        ) : (
          <>
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <Card className="p-6 bg-gradient-to-br from-indigo-50 to-blue-50 border-indigo-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-600 mb-1">Total Visitors</p>
                    <p className="text-3xl font-bold text-slate-900">{stats.totalVisitors}</p>
                    <p className="text-xs text-green-600 mt-1">
                      <TrendingUp size={12} className="inline mr-1" />
                      +12% from last week
                    </p>
                  </div>
                  <div className="bg-indigo-600 p-3 rounded-full">
                    <Users size={24} className="text-white" />
                  </div>
                </div>
              </Card>

              <Card className="p-6 bg-gradient-to-br from-red-50 to-orange-50 border-red-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-600 mb-1">High Intent</p>
                    <p className="text-3xl font-bold text-slate-900">{stats.highIntent}</p>
                    <p className="text-xs text-green-600 mt-1">
                      <TrendingUp size={12} className="inline mr-1" />
                      +8% from last week
                    </p>
                  </div>
                  <div className="bg-red-600 p-3 rounded-full">
                    <MousePointer size={24} className="text-white" />
                  </div>
                </div>
              </Card>

              <Card className="p-6 bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-600 mb-1">New Companies</p>
                    <p className="text-3xl font-bold text-slate-900">{stats.newCompanies}</p>
                    <p className="text-xs text-green-600 mt-1">
                      <TrendingUp size={12} className="inline mr-1" />
                      +15% from last week
                    </p>
                  </div>
                  <div className="bg-green-600 p-3 rounded-full">
                    <Building2 size={24} className="text-white" />
                  </div>
                </div>
              </Card>

              <Card className="p-6 bg-gradient-to-br from-blue-50 to-cyan-50 border-blue-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-slate-600 mb-1">Returning</p>
                    <p className="text-3xl font-bold text-slate-900">{stats.returningCompanies}</p>
                    <p className="text-xs text-green-600 mt-1">
                      <TrendingUp size={12} className="inline mr-1" />
                      +5% from last week
                    </p>
                  </div>
                  <div className="bg-blue-600 p-3 rounded-full">
                    <RefreshCw size={24} className="text-white" />
                  </div>
                </div>
              </Card>
            </div>

            {/* Filters */}
            <Card className="p-4 mb-6">
              <div className="flex items-center gap-4">
                <Filter size={20} className="text-slate-600" />
                <div className="flex gap-2">
                  <span className="text-sm text-slate-600">Intent:</span>
                  {['All', 'High', 'Medium', 'Low'].map(intent => (
                    <button
                      key={intent}
                      onClick={() => setSelectedIntent(intent)}
                      className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                        selectedIntent === intent
                          ? 'bg-indigo-600 text-white'
                          : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                      }`}
                    >
                      {intent}
                    </button>
                  ))}
                </div>
                <div className="flex gap-2 ml-6">
                  <span className="text-sm text-slate-600">Industry:</span>
                  <select
                    value={selectedIndustry}
                    onChange={(e) => setSelectedIndustry(e.target.value)}
                    className="px-3 py-1 rounded border border-slate-300 text-sm"
                  >
                    {industries.map(industry => (
                      <option key={industry} value={industry}>{industry}</option>
                    ))}
                  </select>
                </div>
              </div>
            </Card>

            {/* Visitors Table */}
            <Card className="overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-50 border-b border-slate-200">
                    <tr>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                        Company
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                        Industry
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                        Location
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                        Visit Time
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                        Activity
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                        Intent
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-slate-200">
                    {filteredVisitors.map((visitor) => (
                      <tr key={visitor.id} className="hover:bg-slate-50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="flex items-center">
                              <Building2 size={16} className="text-slate-400 mr-2" />
                              <div className="font-semibold text-slate-900">{visitor.company}</div>
                            </div>
                            <div className="text-xs text-slate-500 mt-1">
                              {visitor.employees} • {visitor.revenue}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm text-slate-700">{visitor.industry}</span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center text-sm text-slate-700">
                            <MapPin size={14} className="text-slate-400 mr-1" />
                            {visitor.location}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center text-sm text-slate-700">
                            <Clock size={14} className="text-slate-400 mr-1" />
                            {formatDateTime(visitor.visitDate)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm">
                            <div className="flex items-center text-slate-700">
                              <Eye size={14} className="text-slate-400 mr-1" />
                              {visitor.pageViews} pages
                            </div>
                            <div className="flex items-center text-slate-500 text-xs mt-1">
                              <Clock size={12} className="text-slate-400 mr-1" />
                              {visitor.duration}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Badge className={`${getIntentBadge(visitor.intent)} border`}>
                            {visitor.intent}
                          </Badge>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Badge className={`${getStatusBadge(visitor.status)} border`}>
                            {visitor.status}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>

            {/* Summary Note */}
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>Note:</strong> This is a mock dashboard displaying static data to demonstrate the website 
                visitor tracking interface. In production, this would integrate with ZoomInfo API to show real-time 
                company visitor data based on IP intelligence.
              </p>
            </div>
          </>
        )}
      </div>
    </Layout>
  );
};

export default WebsiteVisitors;
