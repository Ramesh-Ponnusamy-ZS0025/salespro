import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { toast } from 'sonner';
import { Plus, Sparkles, Loader } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { Card } from '../components/ui/card';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Predefined service options (same as Agent Builder)
const SERVICES = [
  'Quality Engineering',
  'Digital Transformation',
  'Data Engineering',
  'Cloud Services',
  'DevOps',
  'Cybersecurity',
  'AI & Machine Learning',
  'Product Engineering',
  'Consulting',
];

const CampaignBuilder = ({ user, onLogout }) => {
  const [campaigns, setCampaigns] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    campaign_name: '',
    agent_id: '',
    service: '',
    stage: 'TOFU',
    icp: '',
    methodologies: '',
    tone: 'professional',
    resources: '',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [campaignsRes, agentsRes] = await Promise.all([
        axios.get(`${API}/campaigns`),
        axios.get(`${API}/agents`),
      ]);
      setCampaigns(campaignsRes.data);
      setAgents(agentsRes.data);
    } catch (error) {
      toast.error('Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const payload = {
      ...formData,
      icp: formData.icp.split(',').map(i => i.trim()).filter(Boolean),
      methodologies: formData.methodologies.split(',').map(m => m.trim()).filter(Boolean),
      resources: formData.resources.split(',').map(r => r.trim()).filter(Boolean),
    };

    try {
      await axios.post(`${API}/campaigns`, payload);
      toast.success('Campaign created successfully!');
      setShowForm(false);
      resetForm();
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create campaign');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateCopy = async (campaignId) => {
    setGenerating(campaignId);
    try {
      const response = await axios.post(`${API}/campaigns/${campaignId}/generate`);
      toast.success('Campaign copy generated!');
      fetchData();
    } catch (error) {
      toast.error('Failed to generate copy');
    } finally {
      setGenerating(null);
    }
  };

  const handleStatusChange = async (campaignId, status) => {
    try {
      await axios.put(`${API}/campaigns/${campaignId}/status?status=${status}`);
      toast.success('Status updated!');
      fetchData();
    } catch (error) {
      toast.error('Failed to update status');
    }
  };

  const resetForm = () => {
    setFormData({
      campaign_name: '',
      agent_id: '',
      service: '',
      stage: 'TOFU',
      icp: '',
      methodologies: '',
      tone: 'professional',
      resources: '',
    });
  };

  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="p-8" data-testid="campaign-builder-page">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-slate-900 mb-2">Campaign Builder</h1>
            <p className="text-slate-600">Design and manage multi-touch outbound campaigns</p>
          </div>
          <Button
            onClick={() => setShowForm(!showForm)}
            data-testid="toggle-campaign-form"
            className="bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 text-white shadow-lg"
          >
            <Plus size={20} className="mr-2" />
            {showForm ? 'Cancel' : 'Create Campaign'}
          </Button>
        </div>

        {showForm && (
          <Card className="p-6 mb-8 bg-white border border-slate-200 shadow-lg">
            <h3 className="text-lg font-bold text-slate-900 mb-4">New Campaign</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Campaign Name *</Label>
                  <Input
                    data-testid="campaign-name-input"
                    value={formData.campaign_name}
                    onChange={(e) => setFormData({ ...formData, campaign_name: e.target.value })}
                    placeholder="Q1 Digital Transformation Campaign"
                    required
                  />
                </div>
                <div>
                  <Label>Select Agent *</Label>
                  <Select value={formData.agent_id} onValueChange={(value) => setFormData({ ...formData, agent_id: value })} required>
                    <SelectTrigger data-testid="agent-select">
                      <SelectValue placeholder="Choose an agent" />
                    </SelectTrigger>
                    <SelectContent>
                      {agents.map((agent) => (
                        <SelectItem key={agent.id} value={agent.id}>
                          {agent.agent_name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Service *</Label>
                  <Select value={formData.service} onValueChange={(value) => setFormData({ ...formData, service: value })} required>
                    <SelectTrigger data-testid="service-select">
                      <SelectValue placeholder="Select a service" />
                    </SelectTrigger>
                    <SelectContent>
                      {SERVICES.map((service) => (
                        <SelectItem key={service} value={service}>
                          {service}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Funnel Stage *</Label>
                  <Select value={formData.stage} onValueChange={(value) => setFormData({ ...formData, stage: value })}>
                    <SelectTrigger data-testid="stage-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="TOFU">TOFU (Top of Funnel)</SelectItem>
                      <SelectItem value="MOFU">MOFU (Middle of Funnel)</SelectItem>
                      <SelectItem value="BOFU">BOFU (Bottom of Funnel)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div>
                <Label>Target ICP (comma-separated) *</Label>
                <Input
                  value={formData.icp}
                  onChange={(e) => setFormData({ ...formData, icp: e.target.value })}
                  placeholder="Enterprise, Mid-market, Tech companies"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Methodologies (comma-separated)</Label>
                  <Input
                    value={formData.methodologies}
                    onChange={(e) => setFormData({ ...formData, methodologies: e.target.value })}
                    placeholder="KISS, GAP, StoryBrand"
                  />
                </div>
                <div>
                  <Label>Tone</Label>
                  <Select value={formData.tone} onValueChange={(value) => setFormData({ ...formData, tone: value })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="professional">Professional</SelectItem>
                      <SelectItem value="casual">Casual</SelectItem>
                      <SelectItem value="friendly">Friendly</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div>
                <Label>Resources (comma-separated)</Label>
                <Input
                  value={formData.resources}
                  onChange={(e) => setFormData({ ...formData, resources: e.target.value })}
                  placeholder="Case study link, Product demo, Whitepaper"
                />
              </div>
              <Button type="submit" disabled={loading} data-testid="create-campaign-submit" className="w-full">
                {loading ? 'Creating...' : 'Create Campaign'}
              </Button>
            </form>
          </Card>
        )}

        {loading && campaigns.length === 0 ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        ) : campaigns.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-xl border border-slate-200">
            <Sparkles className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-900 mb-2">No campaigns yet</h3>
            <p className="text-slate-600">Create your first campaign to start engaging prospects</p>
          </div>
        ) : (
          <div className="space-y-6">
            {campaigns.map((campaign) => (
              <Card
                key={campaign.id}
                data-testid={`campaign-card-${campaign.id}`}
                className="p-6 bg-white border border-slate-200 shadow-lg hover:shadow-xl transition-shadow duration-200"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-slate-900 mb-2">{campaign.campaign_name}</h3>
                    <div className="flex items-center gap-3 flex-wrap">
                      <Badge className="bg-indigo-100 text-indigo-700">{campaign.service}</Badge>
                      <Badge className="bg-blue-100 text-blue-700">{campaign.stage}</Badge>
                      <Badge
                        className={`${
                          campaign.status === 'published'
                            ? 'bg-green-100 text-green-700'
                            : campaign.status === 'review'
                            ? 'bg-yellow-100 text-yellow-700'
                            : 'bg-slate-100 text-slate-700'
                        }`}
                      >
                        {campaign.status}
                      </Badge>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-xs font-semibold text-slate-700 mb-1">Target ICP:</p>
                    <p className="text-sm text-slate-600">{campaign.icp.join(', ')}</p>
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-slate-700 mb-1">Tone:</p>
                    <p className="text-sm text-slate-600">{campaign.tone}</p>
                  </div>
                </div>

                {campaign.ai_content && (
                  <div className="mb-4 p-4 bg-slate-50 rounded-lg border border-slate-200">
                    <p className="text-xs font-semibold text-slate-700 mb-2">Generated Copy:</p>
                    <p className="text-sm text-slate-800 whitespace-pre-wrap">{campaign.ai_content}</p>
                  </div>
                )}

                <div className="flex gap-2">
                  <Button
                    onClick={() => handleGenerateCopy(campaign.id)}
                    disabled={generating === campaign.id}
                    data-testid={`generate-copy-${campaign.id}`}
                    className="flex-1"
                  >
                    {generating === campaign.id ? (
                      <>
                        <Loader className="animate-spin mr-2" size={16} />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Sparkles size={16} className="mr-2" />
                        {campaign.ai_content ? 'Regenerate' : 'Generate'} Copy
                      </>
                    )}
                  </Button>
                  {campaign.status !== 'published' && (
                    <Button
                      variant="outline"
                      onClick={() => handleStatusChange(campaign.id, 'published')}
                      data-testid={`publish-campaign-${campaign.id}`}
                    >
                      Publish
                    </Button>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default CampaignBuilder;
