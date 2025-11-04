import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { toast } from 'sonner';
import { TrendingUp, Star, MessageSquare, BarChart3, Lightbulb } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Textarea } from '../components/ui/textarea';
import { Label } from '../components/ui/label';
import { Input } from '../components/ui/input';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LearningHub = ({ user, onLogout }) => {
  const [feedback, setFeedback] = useState([]);
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [aiInsights, setAiInsights] = useState('');
  const [feedbackForm, setFeedbackForm] = useState({
    feedback_text: '',
    rating: 5,
    tags: '',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [feedbackRes, insightsRes] = await Promise.all([
        axios.get(`${API}/feedback`),
        axios.get(`${API}/insights`),
      ]);
      setFeedback(feedbackRes.data);
      setInsights(insightsRes.data);
    } catch (error) {
      toast.error('Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitFeedback = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    const payload = {
      ...feedbackForm,
      rating: parseInt(feedbackForm.rating),
      tags: feedbackForm.tags.split(',').map(t => t.trim()).filter(Boolean),
    };

    try {
      await axios.post(`${API}/feedback`, payload);
      toast.success('Feedback submitted successfully!');
      setFeedbackForm({ feedback_text: '', rating: 5, tags: '' });
      fetchData();
    } catch (error) {
      toast.error('Failed to submit feedback');
    } finally {
      setSubmitting(false);
    }
  };

  const handleRunInsights = async () => {
    setGenerating(true);
    try {
      const response = await axios.post(`${API}/insights/run`);
      setAiInsights(response.data.insights);
      toast.success('AI insights generated!');
      fetchData();
    } catch (error) {
      toast.error('Failed to generate insights');
    } finally {
      setGenerating(false);
    }
  };

  const averageRating = feedback.length > 0
    ? (feedback.reduce((sum, fb) => sum + fb.rating, 0) / feedback.length).toFixed(1)
    : '0.0';

  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="p-8" data-testid="learning-hub-page">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-slate-900 mb-2">Learning & Feedback Hub</h1>
            <p className="text-slate-600">Aggregate insights and improve campaign performance</p>
          </div>

          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card className="p-6 bg-gradient-to-br from-indigo-50 to-blue-50 border border-indigo-100">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-indigo-600 rounded-lg flex items-center justify-center">
                  <MessageSquare className="text-white" size={24} />
                </div>
                <div>
                  <p className="text-2xl font-bold text-indigo-900">{feedback.length}</p>
                  <p className="text-sm text-indigo-700">Total Feedback</p>
                </div>
              </div>
            </Card>
            <Card className="p-6 bg-gradient-to-br from-yellow-50 to-orange-50 border border-yellow-100">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-yellow-600 rounded-lg flex items-center justify-center">
                  <Star className="text-white" size={24} />
                </div>
                <div>
                  <p className="text-2xl font-bold text-yellow-900">{averageRating}</p>
                  <p className="text-sm text-yellow-700">Average Rating</p>
                </div>
              </div>
            </Card>
            <Card className="p-6 bg-gradient-to-br from-green-50 to-emerald-50 border border-green-100">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center">
                  <Lightbulb className="text-white" size={24} />
                </div>
                <div>
                  <p className="text-2xl font-bold text-green-900">{insights.length}</p>
                  <p className="text-sm text-green-700">Active Insights</p>
                </div>
              </div>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Submit Feedback */}
            <Card className="p-6 bg-white border border-slate-200 shadow-lg">
              <h3 className="text-lg font-bold text-slate-900 mb-4">Submit Feedback</h3>
              <form onSubmit={handleSubmitFeedback} className="space-y-4">
                <div>
                  <Label>Feedback *</Label>
                  <Textarea
                    data-testid="feedback-input"
                    value={feedbackForm.feedback_text}
                    onChange={(e) => setFeedbackForm({ ...feedbackForm, feedback_text: e.target.value })}
                    placeholder="Share your thoughts on campaigns, agents, or platform features..."
                    rows={4}
                    required
                  />
                </div>
                <div>
                  <Label>Rating (1-5) *</Label>
                  <Input
                    type="number"
                    min="1"
                    max="5"
                    data-testid="rating-input"
                    value={feedbackForm.rating}
                    onChange={(e) => setFeedbackForm({ ...feedbackForm, rating: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <Label>Tags (comma-separated)</Label>
                  <Input
                    value={feedbackForm.tags}
                    onChange={(e) => setFeedbackForm({ ...feedbackForm, tags: e.target.value })}
                    placeholder="campaign, agent, ui, feature-request"
                  />
                </div>
                <Button type="submit" disabled={submitting} data-testid="submit-feedback-button" className="w-full">
                  {submitting ? 'Submitting...' : 'Submit Feedback'}
                </Button>
              </form>
            </Card>

            {/* AI Insights Generator */}
            <Card className="p-6 bg-white border border-slate-200 shadow-lg">
              <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
                <BarChart3 className="text-indigo-600" />
                AI-Powered Insights
              </h3>
              <div className="space-y-4">
                <p className="text-sm text-slate-600">
                  Generate AI-powered insights based on your platform data, feedback, and campaign performance.
                </p>
                <Button
                  onClick={handleRunInsights}
                  disabled={generating}
                  data-testid="run-insights-button"
                  className="w-full"
                >
                  {generating ? 'Generating...' : 'Run Insights Engine'}
                </Button>
                {aiInsights && (
                  <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                    <p className="text-sm text-slate-800 whitespace-pre-wrap" data-testid="ai-insights">
                      {aiInsights}
                    </p>
                  </div>
                )}
              </div>
            </Card>
          </div>

          {/* Insights List */}
          <Card className="p-6 bg-white border border-slate-200 shadow-lg mb-8">
            <h3 className="text-lg font-bold text-slate-900 mb-4">System Insights</h3>
            {insights.length > 0 ? (
              <div className="space-y-3">
                {insights.map((insight) => (
                  <div key={insight.id} className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                    <div className="flex items-start justify-between mb-2">
                      <Badge className="bg-indigo-100 text-indigo-700">{insight.metric}</Badge>
                      <Badge
                        className={`${
                          insight.status === 'active'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-slate-100 text-slate-700'
                        }`}
                      >
                        {insight.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-slate-800 font-medium mb-2">{insight.observation}</p>
                    <p className="text-sm text-indigo-600">
                      <strong>Action:</strong> {insight.suggested_action}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <TrendingUp className="w-12 h-12 text-slate-300 mx-auto mb-2" />
                <p className="text-slate-600">No insights available yet. Submit more feedback to generate insights!</p>
              </div>
            )}
          </Card>

          {/* Recent Feedback */}
          <Card className="p-6 bg-white border border-slate-200 shadow-lg">
            <h3 className="text-lg font-bold text-slate-900 mb-4">Recent Feedback</h3>
            {feedback.length > 0 ? (
              <div className="space-y-3">
                {feedback.slice(0, 5).map((fb) => (
                  <div key={fb.id} className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {[...Array(5)].map((_, i) => (
                          <Star
                            key={i}
                            size={16}
                            className={i < fb.rating ? 'text-yellow-500 fill-yellow-500' : 'text-slate-300'}
                          />
                        ))}
                      </div>
                      {fb.tags.length > 0 && (
                        <div className="flex gap-1">
                          {fb.tags.map((tag, idx) => (
                            <Badge key={idx} variant="outline" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                    <p className="text-sm text-slate-700">{fb.feedback_text}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <MessageSquare className="w-12 h-12 text-slate-300 mx-auto mb-2" />
                <p className="text-slate-600">No feedback yet. Be the first to share your thoughts!</p>
              </div>
            )}
          </Card>
        </div>
      </div>
    </Layout>
  );
};

export default LearningHub;
