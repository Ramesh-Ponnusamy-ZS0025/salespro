import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { toast } from 'sonner';
import { Plus, Calendar, ChevronDown, ChevronUp, Edit2, Trash2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../components/ui/dialog';
import { Card } from '../components/ui/card';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ZuciNews = ({ user, onLogout }) => {
  const [newsList, setNewsList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [expandedNewsId, setExpandedNewsId] = useState(null);
  const [editingNews, setEditingNews] = useState(null);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    published_date: new Date().toISOString().split('T')[0], // YYYY-MM-DD
    news_link: ''
  });

  useEffect(() => {
    fetchNews();
  }, []);

  const fetchNews = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/zuci-news`);
      setNewsList(response.data);
    } catch (error) {
      toast.error('Failed to load news');
      console.error('Error fetching news:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!formData.title || !formData.description || !formData.published_date) {
      toast.error('Please fill in all fields');
      return;
    }

    try {
      if (editingNews) {
        // Update existing news
        await axios.put(`${API}/zuci-news/${editingNews.id}`, formData);
        toast.success('News updated successfully!');
      } else {
        // Create new news
        await axios.post(`${API}/zuci-news`, formData);
        toast.success('News created successfully!');
      }

      setShowCreateModal(false);
      setEditingNews(null);
      setFormData({
        title: '',
        description: '',
        published_date: new Date().toISOString().split('T')[0],
        news_link: ''
      });
      fetchNews();
    } catch (error) {
      toast.error(editingNews ? 'Failed to update news' : 'Failed to create news');
      console.error('Error saving news:', error);
    }
  };

  const handleEdit = (news) => {
    setEditingNews(news);
    setFormData({
      title: news.title,
      description: news.description,
      published_date: news.published_date,
      news_link: news.news_link || ''
    });
    setShowCreateModal(true);
  };

  const handleDelete = async (newsId) => {
    if (!window.confirm('Are you sure you want to delete this news?')) {
      return;
    }

    try {
      await axios.delete(`${API}/zuci-news/${newsId}`);
      toast.success('News deleted successfully!');
      fetchNews();
    } catch (error) {
      toast.error('Failed to delete news');
      console.error('Error deleting news:', error);
    }
  };

  const toggleExpand = (newsId) => {
    setExpandedNewsId(expandedNewsId === newsId ? null : newsId);
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
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">Zuci News</h1>
              <p className="text-slate-600 mt-1">Manage company news and announcements</p>
            </div>
            <Button
              onClick={() => {
                setEditingNews(null);
                setFormData({
                  title: '',
                  description: '',
                  published_date: new Date().toISOString().split('T')[0],
                  news_link: ''
                });
                setShowCreateModal(true);
              }}
              className="bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700"
            >
              <Plus size={16} className="mr-2" />
              Create New Zuci News
            </Button>
          </div>

          {/* News List */}
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
          ) : newsList.length === 0 ? (
            <Card className="p-12 text-center bg-slate-50">
              <p className="text-slate-600 text-lg mb-4">No news articles yet</p>
              <p className="text-slate-500 text-sm">Click "Create New Zuci News" to get started</p>
            </Card>
          ) : (
            <div className="space-y-3">
              {newsList.map((news) => (
                <Card
                  key={news.id}
                  className="overflow-hidden hover:shadow-md transition-shadow"
                >
                  {/* Collapsed View - Clickable Header */}
                  <div
                    onClick={() => toggleExpand(news.id)}
                    className="p-4 cursor-pointer hover:bg-slate-50 transition-colors flex items-center justify-between"
                  >
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-slate-900 mb-1">
                        {news.title}
                      </h3>
                      <div className="flex items-center text-sm text-slate-600">
                        <Calendar size={14} className="mr-1" />
                        {formatDate(news.published_date)}
                      </div>
                    </div>
                    <div className="ml-4 text-slate-400">
                      {expandedNewsId === news.id ? (
                        <ChevronUp size={20} />
                      ) : (
                        <ChevronDown size={20} />
                      )}
                    </div>
                  </div>

                  {/* Expanded View - Details */}
                  {expandedNewsId === news.id && (
                    <div className="border-t border-slate-200 bg-slate-50 p-4">
                      <div className="mb-4">
                        <Label className="text-sm font-semibold text-slate-700 mb-2 block">
                          Description
                        </Label>
                        <p className="text-slate-800 whitespace-pre-wrap leading-relaxed">
                          {news.description}
                        </p>
                      </div>

                      {news.news_link && (
                        <div className="mb-4">
                          <Label className="text-sm font-semibold text-slate-700 mb-2 block">
                            News Link
                          </Label>
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

                      <div className="flex items-center justify-between pt-4 border-t border-slate-200">
                        <div className="text-xs text-slate-500">
                          Created: {formatDate(news.created_at)}
                        </div>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleEdit(news);
                            }}
                          >
                            <Edit2 size={14} className="mr-1" />
                            Edit
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDelete(news.id);
                            }}
                          >
                            <Trash2 size={14} className="mr-1" />
                            Delete
                          </Button>
                        </div>
                      </div>
                    </div>
                  )}
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Create/Edit Modal */}
      <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {editingNews ? 'Edit Zuci News' : 'Create New Zuci News'}
            </DialogTitle>
            <DialogDescription>
              {editingNews
                ? 'Update the news article details below'
                : 'Fill in the details to create a new news article'
              }
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div>
              <Label>News Title *</Label>
              <Input
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Enter news title"
                className="mt-1"
              />
            </div>

            <div>
              <Label>Published Date *</Label>
              <Input
                type="date"
                value={formData.published_date}
                onChange={(e) => setFormData({ ...formData, published_date: e.target.value })}
                className="mt-1"
              />
            </div>

            <div>
              <Label>News Link (Optional)</Label>
              <Input
                type="url"
                value={formData.news_link}
                onChange={(e) => setFormData({ ...formData, news_link: e.target.value })}
                placeholder="https://example.com/news-article"
                className="mt-1"
              />
              <p className="text-xs text-slate-500 mt-1">
                Add a link to the full news article or announcement
              </p>
            </div>

            <div>
              <Label>News Description *</Label>
              <Textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Enter detailed description of the news"
                rows={8}
                className="mt-1"
              />
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={() => {
                setShowCreateModal(false);
                setEditingNews(null);
                setFormData({
                  title: '',
                  description: '',
                  published_date: new Date().toISOString().split('T')[0],
                  news_link: ''
                });
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleCreate}
              className="bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700"
            >
              {editingNews ? 'Update News' : 'Create News'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </Layout>
  );
};

export default ZuciNews;
