import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { toast } from 'sonner';
import { Plus, Calendar, ChevronDown, ChevronUp, Edit2, Trash2, X } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../components/ui/dialog';
import { Card } from '../components/ui/card';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ZuciNews = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState('news');

  // Zuci News State
  const [newsList, setNewsList] = useState([]);
  const [newsLoading, setNewsLoading] = useState(true);
  const [showNewsModal, setShowNewsModal] = useState(false);
  const [expandedNewsId, setExpandedNewsId] = useState(null);
  const [editingNews, setEditingNews] = useState(null);
  const [newsFormData, setNewsFormData] = useState({
    title: '',
    description: '',
    published_date: new Date().toISOString().split('T')[0],
    news_link: ''
  });

  // Zuci Wins State
  const [winsList, setWinsList] = useState([]);
  const [winsLoading, setWinsLoading] = useState(true);
  const [showWinsModal, setShowWinsModal] = useState(false);
  const [expandedWinId, setExpandedWinId] = useState(null);
  const [editingWin, setEditingWin] = useState(null);
  const [winsFormData, setWinsFormData] = useState({
    company_name: '',
    description: '',
    win_date: new Date().toISOString().split('T')[0],
    contributions: []
  });

  // GTM State
  const [gtmList, setGtmList] = useState([]);
  const [gtmLoading, setGtmLoading] = useState(true);
  const [showGtmModal, setShowGtmModal] = useState(false);
  const [expandedGtmId, setExpandedGtmId] = useState(null);
  const [editingGtm, setEditingGtm] = useState(null);
  const [gtmFormData, setGtmFormData] = useState({
    gtm_link: '',
    description: '',
    prospect_name: '',
    date: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    if (activeTab === 'news') {
      fetchNews();
    } else if (activeTab === 'wins') {
      fetchWins();
    } else if (activeTab === 'gtm') {
      fetchGtm();
    }
  }, [activeTab]);

  // ============== ZUCI NEWS FUNCTIONS ==============

  const fetchNews = async () => {
    try {
      setNewsLoading(true);
      const response = await axios.get(`${API}/zuci-news`);
      setNewsList(response.data);
    } catch (error) {
      toast.error('Failed to load news');
      console.error('Error fetching news:', error);
    } finally {
      setNewsLoading(false);
    }
  };

  const handleNewsSubmit = async () => {
    if (!newsFormData.title || !newsFormData.description || !newsFormData.published_date) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      if (editingNews) {
        await axios.put(`${API}/zuci-news/${editingNews.id}`, newsFormData);
        toast.success('News updated successfully!');
      } else {
        await axios.post(`${API}/zuci-news`, newsFormData);
        toast.success('News created successfully!');
      }
      setShowNewsModal(false);
      setEditingNews(null);
      resetNewsForm();
      fetchNews();
    } catch (error) {
      toast.error(editingNews ? 'Failed to update news' : 'Failed to create news');
    }
  };

  const handleNewsEdit = (news) => {
    setEditingNews(news);
    setNewsFormData({
      title: news.title,
      description: news.description,
      published_date: news.published_date,
      news_link: news.news_link || ''
    });
    setShowNewsModal(true);
  };

  const handleNewsDelete = async (newsId) => {
    if (!window.confirm('Are you sure you want to delete this news?')) return;
    try {
      await axios.delete(`${API}/zuci-news/${newsId}`);
      toast.success('News deleted successfully!');
      fetchNews();
    } catch (error) {
      toast.error('Failed to delete news');
    }
  };

  const resetNewsForm = () => {
    setNewsFormData({
      title: '',
      description: '',
      published_date: new Date().toISOString().split('T')[0],
      news_link: ''
    });
  };

  // ============== ZUCI WINS FUNCTIONS ==============

  const fetchWins = async () => {
    try {
      setWinsLoading(true);
      const response = await axios.get(`${API}/zuci-wins`);
      setWinsList(response.data);
    } catch (error) {
      toast.error('Failed to load wins');
      console.error('Error fetching wins:', error);
    } finally {
      setWinsLoading(false);
    }
  };

  const handleWinsSubmit = async () => {
    if (!winsFormData.company_name || !winsFormData.description || !winsFormData.win_date) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      if (editingWin) {
        await axios.put(`${API}/zuci-wins/${editingWin.id}`, winsFormData);
        toast.success('Win updated successfully!');
      } else {
        await axios.post(`${API}/zuci-wins`, winsFormData);
        toast.success('Win created successfully!');
      }
      setShowWinsModal(false);
      setEditingWin(null);
      resetWinsForm();
      fetchWins();
    } catch (error) {
      toast.error(editingWin ? 'Failed to update win' : 'Failed to create win');
    }
  };

  const handleWinsEdit = (win) => {
    setEditingWin(win);
    setWinsFormData({
      company_name: win.company_name,
      description: win.description,
      win_date: win.win_date,
      contributions: win.contributions || []
    });
    setShowWinsModal(true);
  };

  const handleWinsDelete = async (winId) => {
    if (!window.confirm('Are you sure you want to delete this win?')) return;
    try {
      await axios.delete(`${API}/zuci-wins/${winId}`);
      toast.success('Win deleted successfully!');
      fetchWins();
    } catch (error) {
      toast.error('Failed to delete win');
    }
  };

  const resetWinsForm = () => {
    setWinsFormData({
      company_name: '',
      description: '',
      win_date: new Date().toISOString().split('T')[0],
      contributions: []
    });
  };

  const addContributor = () => {
    setWinsFormData({
      ...winsFormData,
      contributions: [...winsFormData.contributions, { name: '', email: '', designation: '' }]
    });
  };

  const updateContributor = (index, field, value) => {
    const updatedContributions = [...winsFormData.contributions];
    updatedContributions[index][field] = value;
    setWinsFormData({ ...winsFormData, contributions: updatedContributions });
  };

  const removeContributor = (index) => {
    const updatedContributions = winsFormData.contributions.filter((_, i) => i !== index);
    setWinsFormData({ ...winsFormData, contributions: updatedContributions });
  };

  // ============== GTM FUNCTIONS ==============

  const fetchGtm = async () => {
    try {
      setGtmLoading(true);
      const response = await axios.get(`${API}/gtm-entries`);
      setGtmList(response.data);
    } catch (error) {
      toast.error('Failed to load GTM entries');
      console.error('Error fetching GTM:', error);
    } finally {
      setGtmLoading(false);
    }
  };

  const handleGtmSubmit = async () => {
    if (!gtmFormData.gtm_link || !gtmFormData.description || !gtmFormData.prospect_name || !gtmFormData.date) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      if (editingGtm) {
        await axios.put(`${API}/gtm-entries/${editingGtm.id}`, gtmFormData);
        toast.success('GTM entry updated successfully!');
      } else {
        await axios.post(`${API}/gtm-entries`, gtmFormData);
        toast.success('GTM entry created successfully!');
      }
      setShowGtmModal(false);
      setEditingGtm(null);
      resetGtmForm();
      fetchGtm();
    } catch (error) {
      toast.error(editingGtm ? 'Failed to update GTM entry' : 'Failed to create GTM entry');
    }
  };

  const handleGtmEdit = (gtm) => {
    setEditingGtm(gtm);
    setGtmFormData({
      gtm_link: gtm.gtm_link,
      description: gtm.description,
      prospect_name: gtm.prospect_name,
      date: gtm.date
    });
    setShowGtmModal(true);
  };

  const handleGtmDelete = async (gtmId) => {
    if (!window.confirm('Are you sure you want to delete this GTM entry?')) return;
    try {
      await axios.delete(`${API}/gtm-entries/${gtmId}`);
      toast.success('GTM entry deleted successfully!');
      fetchGtm();
    } catch (error) {
      toast.error('Failed to delete GTM entry');
    }
  };

  const resetGtmForm = () => {
    setGtmFormData({
      gtm_link: '',
      description: '',
      prospect_name: '',
      date: new Date().toISOString().split('T')[0]
    });
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="p-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-slate-900">Content Management</h1>
            <p className="text-slate-600 mt-1">Manage Zuci News, Wins, and GTM entries</p>
          </div>

          {/* Tab Navigation */}
          <div className="flex items-center gap-4 mb-6 border-b border-slate-200">
            <button
              onClick={() => setActiveTab('news')}
              className={`px-6 py-3 font-semibold transition-colors relative ${
                activeTab === 'news'
                  ? 'text-indigo-600 border-b-2 border-indigo-600'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Zuci News
            </button>
            <button
              onClick={() => setActiveTab('wins')}
              className={`px-6 py-3 font-semibold transition-colors relative ${
                activeTab === 'wins'
                  ? 'text-indigo-600 border-b-2 border-indigo-600'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Zuci Wins
            </button>
            <button
              onClick={() => setActiveTab('gtm')}
              className={`px-6 py-3 font-semibold transition-colors relative ${
                activeTab === 'gtm'
                  ? 'text-indigo-600 border-b-2 border-indigo-600'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              GTM
            </button>
          </div>

          {/* Tab Content */}
          {activeTab === 'news' && (
            <div>
              {/* Header with Create Button */}
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-slate-900">Zuci News Articles</h2>
                <Button
                  onClick={() => {
                    setEditingNews(null);
                    resetNewsForm();
                    setShowNewsModal(true);
                  }}
                  className="bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700"
                >
                  <Plus size={16} className="mr-2" />
                  Create News
                </Button>
              </div>

              {/* News List */}
              {newsLoading ? (
                <div className="flex items-center justify-center h-64">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
                </div>
              ) : newsList.length === 0 ? (
                <Card className="p-12 text-center bg-slate-50">
                  <p className="text-slate-600">No news articles yet</p>
                </Card>
              ) : (
                <div className="space-y-3">
                  {newsList.map((news) => (
                    <Card key={news.id} className="overflow-hidden hover:shadow-md transition-shadow">
                      <div
                        onClick={() => setExpandedNewsId(expandedNewsId === news.id ? null : news.id)}
                        className="p-4 cursor-pointer hover:bg-slate-50 transition-colors flex items-center justify-between"
                      >
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-slate-900 mb-1">{news.title}</h3>
                          <div className="flex items-center text-sm text-slate-600">
                            <Calendar size={14} className="mr-1" />
                            {formatDate(news.published_date)}
                          </div>
                        </div>
                        <div className="ml-4 text-slate-400">
                          {expandedNewsId === news.id ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                        </div>
                      </div>

                      {expandedNewsId === news.id && (
                        <div className="border-t border-slate-200 bg-slate-50 p-4">
                          <div className="mb-4">
                            <Label className="text-sm font-semibold text-slate-700 mb-2 block">Description</Label>
                            <p className="text-slate-800 whitespace-pre-wrap">{news.description}</p>
                          </div>
                          {news.news_link && (
                            <div className="mb-4">
                              <Label className="text-sm font-semibold text-slate-700 mb-2 block">News Link</Label>
                              <a
                                href={news.news_link}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-indigo-600 hover:text-indigo-800 underline break-all"
                              >
                                {news.news_link}
                              </a>
                            </div>
                          )}
                          <div className="flex items-center justify-end gap-2 pt-4 border-t border-slate-200">
                            <Button size="sm" variant="outline" onClick={() => handleNewsEdit(news)}>
                              <Edit2 size={14} className="mr-1" />
                              Edit
                            </Button>
                            <Button size="sm" variant="destructive" onClick={() => handleNewsDelete(news.id)}>
                              <Trash2 size={14} className="mr-1" />
                              Delete
                            </Button>
                          </div>
                        </div>
                      )}
                    </Card>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'wins' && (
            <div>
              {/* Header with Create Button */}
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-slate-900">Zuci Wins</h2>
                <Button
                  onClick={() => {
                    setEditingWin(null);
                    resetWinsForm();
                    setShowWinsModal(true);
                  }}
                  className="bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700"
                >
                  <Plus size={16} className="mr-2" />
                  Add Zuci Wins
                </Button>
              </div>

              {/* Wins List */}
              {winsLoading ? (
                <div className="flex items-center justify-center h-64">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
                </div>
              ) : winsList.length === 0 ? (
                <Card className="p-12 text-center bg-slate-50">
                  <p className="text-slate-600">No wins yet</p>
                </Card>
              ) : (
                <div className="space-y-3">
                  {winsList.map((win) => (
                    <Card key={win.id} className="overflow-hidden hover:shadow-md transition-shadow">
                      <div
                        onClick={() => setExpandedWinId(expandedWinId === win.id ? null : win.id)}
                        className="p-4 cursor-pointer hover:bg-slate-50 transition-colors flex items-center justify-between"
                      >
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-slate-900 mb-1">{win.company_name}</h3>
                          <div className="flex items-center text-sm text-slate-600">
                            <Calendar size={14} className="mr-1" />
                            {formatDate(win.win_date)}
                          </div>
                        </div>
                        <div className="ml-4 text-slate-400">
                          {expandedWinId === win.id ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                        </div>
                      </div>

                      {expandedWinId === win.id && (
                        <div className="border-t border-slate-200 bg-slate-50 p-4">
                          <div className="mb-4">
                            <Label className="text-sm font-semibold text-slate-700 mb-2 block">Description</Label>
                            <p className="text-slate-800 whitespace-pre-wrap">{win.description}</p>
                          </div>
                          {win.contributions && win.contributions.length > 0 && (
                            <div className="mb-4">
                              <Label className="text-sm font-semibold text-slate-700 mb-2 block">Contributors</Label>
                              <div className="space-y-2">
                                {win.contributions.map((contrib, idx) => (
                                  <div key={idx} className="p-3 bg-white rounded border border-slate-200">
                                    <p className="font-medium text-slate-900">{contrib.name}</p>
                                    <p className="text-sm text-slate-600">{contrib.designation}</p>
                                    <p className="text-sm text-slate-500">{contrib.email}</p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                          <div className="flex items-center justify-end gap-2 pt-4 border-t border-slate-200">
                            <Button size="sm" variant="outline" onClick={() => handleWinsEdit(win)}>
                              <Edit2 size={14} className="mr-1" />
                              Edit
                            </Button>
                            <Button size="sm" variant="destructive" onClick={() => handleWinsDelete(win.id)}>
                              <Trash2 size={14} className="mr-1" />
                              Delete
                            </Button>
                          </div>
                        </div>
                      )}
                    </Card>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'gtm' && (
            <div>
              {/* Header with Create Button */}
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-slate-900">GTM Entries</h2>
                <Button
                  onClick={() => {
                    setEditingGtm(null);
                    resetGtmForm();
                    setShowGtmModal(true);
                  }}
                  className="bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700"
                >
                  <Plus size={16} className="mr-2" />
                  Add GTM Entry
                </Button>
              </div>

              {/* GTM List */}
              {gtmLoading ? (
                <div className="flex items-center justify-center h-64">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
                </div>
              ) : gtmList.length === 0 ? (
                <Card className="p-12 text-center bg-slate-50">
                  <p className="text-slate-600">No GTM entries yet</p>
                </Card>
              ) : (
                <div className="space-y-3">
                  {gtmList.map((gtm) => (
                    <Card key={gtm.id} className="overflow-hidden hover:shadow-md transition-shadow">
                      <div
                        onClick={() => setExpandedGtmId(expandedGtmId === gtm.id ? null : gtm.id)}
                        className="p-4 cursor-pointer hover:bg-slate-50 transition-colors flex items-center justify-between"
                      >
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-slate-900 mb-1">{gtm.prospect_name}</h3>
                          <div className="flex items-center text-sm text-slate-600">
                            <Calendar size={14} className="mr-1" />
                            {formatDate(gtm.date)}
                          </div>
                        </div>
                        <div className="ml-4 text-slate-400">
                          {expandedGtmId === gtm.id ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                        </div>
                      </div>

                      {expandedGtmId === gtm.id && (
                        <div className="border-t border-slate-200 bg-slate-50 p-4">
                          <div className="mb-4">
                            <Label className="text-sm font-semibold text-slate-700 mb-2 block">Description</Label>
                            <p className="text-slate-800 whitespace-pre-wrap">{gtm.description}</p>
                          </div>
                          <div className="mb-4">
                            <Label className="text-sm font-semibold text-slate-700 mb-2 block">GTM Link</Label>
                            <a
                              href={gtm.gtm_link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-indigo-600 hover:text-indigo-800 underline break-all"
                            >
                              {gtm.gtm_link}
                            </a>
                          </div>
                          <div className="flex items-center justify-end gap-2 pt-4 border-t border-slate-200">
                            <Button size="sm" variant="outline" onClick={() => handleGtmEdit(gtm)}>
                              <Edit2 size={14} className="mr-1" />
                              Edit
                            </Button>
                            <Button size="sm" variant="destructive" onClick={() => handleGtmDelete(gtm.id)}>
                              <Trash2 size={14} className="mr-1" />
                              Delete
                            </Button>
                          </div>
                        </div>
                      )}
                    </Card>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Zuci News Modal */}
      <Dialog open={showNewsModal} onOpenChange={setShowNewsModal}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{editingNews ? 'Edit Zuci News' : 'Create New Zuci News'}</DialogTitle>
            <DialogDescription>
              {editingNews ? 'Update the news article details' : 'Fill in the details to create a new news article'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div>
              <Label>News Title *</Label>
              <Input
                value={newsFormData.title}
                onChange={(e) => setNewsFormData({ ...newsFormData, title: e.target.value })}
                placeholder="Enter news title"
              />
            </div>
            <div>
              <Label>Published Date *</Label>
              <Input
                type="date"
                value={newsFormData.published_date}
                onChange={(e) => setNewsFormData({ ...newsFormData, published_date: e.target.value })}
              />
            </div>
            <div>
              <Label>News Link (Optional)</Label>
              <Input
                type="url"
                value={newsFormData.news_link}
                onChange={(e) => setNewsFormData({ ...newsFormData, news_link: e.target.value })}
                placeholder="https://example.com/news-article"
              />
            </div>
            <div>
              <Label>News Description *</Label>
              <Textarea
                value={newsFormData.description}
                onChange={(e) => setNewsFormData({ ...newsFormData, description: e.target.value })}
                placeholder="Enter detailed description"
                rows={6}
              />
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setShowNewsModal(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleNewsSubmit}
              className="bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700"
            >
              {editingNews ? 'Update News' : 'Create News'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Zuci Wins Modal */}
      <Dialog open={showWinsModal} onOpenChange={setShowWinsModal}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editingWin ? 'Edit Zuci Win' : 'Add New Zuci Win'}</DialogTitle>
            <DialogDescription>
              {editingWin ? 'Update the win details' : 'Fill in the details to add a new win'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div>
              <Label>Company Name *</Label>
              <Input
                value={winsFormData.company_name}
                onChange={(e) => setWinsFormData({ ...winsFormData, company_name: e.target.value })}
                placeholder="Enter company name"
              />
            </div>
            <div>
              <Label>Win Date *</Label>
              <Input
                type="date"
                value={winsFormData.win_date}
                onChange={(e) => setWinsFormData({ ...winsFormData, win_date: e.target.value })}
              />
            </div>
            <div>
              <Label>Description *</Label>
              <Textarea
                value={winsFormData.description}
                onChange={(e) => setWinsFormData({ ...winsFormData, description: e.target.value })}
                placeholder="Enter win description"
                rows={4}
              />
            </div>

            {/* Contributors Section */}
            <div className="border-t pt-4">
              <div className="flex items-center justify-between mb-3">
                <Label className="text-base font-semibold">Contributors</Label>
                <Button type="button" size="sm" variant="outline" onClick={addContributor}>
                  <Plus size={14} className="mr-1" />
                  Add Contributor
                </Button>
              </div>

              <div className="space-y-3">
                {winsFormData.contributions.map((contrib, index) => (
                  <Card key={index} className="p-4 bg-slate-50">
                    <div className="flex items-start justify-between mb-3">
                      <Label className="text-sm font-semibold">Contributor {index + 1}</Label>
                      <Button
                        type="button"
                        size="sm"
                        variant="ghost"
                        onClick={() => removeContributor(index)}
                      >
                        <X size={16} />
                      </Button>
                    </div>
                    <div className="grid grid-cols-1 gap-3">
                      <Input
                        placeholder="Name"
                        value={contrib.name}
                        onChange={(e) => updateContributor(index, 'name', e.target.value)}
                      />
                      <Input
                        placeholder="Email"
                        type="email"
                        value={contrib.email}
                        onChange={(e) => updateContributor(index, 'email', e.target.value)}
                      />
                      <Input
                        placeholder="Designation"
                        value={contrib.designation}
                        onChange={(e) => updateContributor(index, 'designation', e.target.value)}
                      />
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setShowWinsModal(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleWinsSubmit}
              className="bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700"
            >
              {editingWin ? 'Update Win' : 'Add Win'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* GTM Modal */}
      <Dialog open={showGtmModal} onOpenChange={setShowGtmModal}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{editingGtm ? 'Edit GTM Entry' : 'Add New GTM Entry'}</DialogTitle>
            <DialogDescription>
              {editingGtm ? 'Update the GTM entry details' : 'Fill in the details to add a new GTM entry'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div>
              <Label>Prospect Name *</Label>
              <Input
                value={gtmFormData.prospect_name}
                onChange={(e) => setGtmFormData({ ...gtmFormData, prospect_name: e.target.value })}
                placeholder="Enter prospect name"
              />
            </div>
            <div>
              <Label>Date *</Label>
              <Input
                type="date"
                value={gtmFormData.date}
                onChange={(e) => setGtmFormData({ ...gtmFormData, date: e.target.value })}
              />
            </div>
            <div>
              <Label>GTM Link *</Label>
              <Input
                type="url"
                value={gtmFormData.gtm_link}
                onChange={(e) => setGtmFormData({ ...gtmFormData, gtm_link: e.target.value })}
                placeholder="https://example.com/gtm-link"
              />
            </div>
            <div>
              <Label>Description *</Label>
              <Textarea
                value={gtmFormData.description}
                onChange={(e) => setGtmFormData({ ...gtmFormData, description: e.target.value })}
                placeholder="Enter GTM description"
                rows={4}
              />
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setShowGtmModal(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleGtmSubmit}
              className="bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700"
            >
              {editingGtm ? 'Update Entry' : 'Add Entry'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </Layout>
  );
};

export default ZuciNews;
