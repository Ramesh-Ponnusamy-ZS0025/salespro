import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { toast } from 'sonner';
import { Plus, ArrowRight, Mail, MessageSquare, Phone, Filter, Megaphone } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Card } from '../components/ui/card';
import CampaignTimeline from '../components/CampaignTimeline';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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

const FUNNEL_STAGES = [
  { value: 'TOFU', label: 'Top of Funnel', description: 'Awareness & Education' },
  { value: 'MOFU', label: 'Middle of Funnel', description: 'Consideration & Evaluation' },
  { value: 'BOFU', label: 'Bottom of Funnel', description: 'Decision & Purchase' },
];

const CampaignBuilder = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [campaigns, setCampaigns] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentStep, setCurrentStep] = useState('list'); // list, config, timeline
  const [selectedCampaign, setSelectedCampaign] = useState(null);
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
  const [touchpointConfig, setTouchpointConfig] = useState({
    total_touchpoints: 7,
    email_count: 4,
    linkedin_count: 2,
    voicemail_count: 1,
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

  const handleAgentSelect = (agentId) => {
    const selectedAgent = agents.find(agent => agent.id === agentId);
    if (selectedAgent) {
      setFormData(prev => ({
        ...prev,
        agent_id: agentId,
        service: selectedAgent.service || prev.service,
        tone: selectedAgent.tone || prev.tone,
        methodologies: selectedAgent.methodologies?.join(', ') || prev.methodologies,
        icp: selectedAgent.personas?.join(', ') || prev.icp,
      }));
      toast.success(`Agent "${selectedAgent.agent_name}" configuration loaded!`);
    } else {
      setFormData(prev => ({ ...prev, agent_id: agentId }));
    }
  };

  const handleCreateCampaign = () => {
    setCurrentStep('config');
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

  const handleConfigSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const payload = {
      ...formData,
      icp: formData.icp.split(',').map(i => i.trim()).filter(Boolean),
      methodologies: formData.methodologies.split(',').map(m => m.trim()).filter(Boolean),
      resources: formData.resources.split(',').map(r => r.trim()).filter(Boolean),
    };

    try {
      const campaignRes = await axios.post(`${API}/campaigns`, payload);
      const newCampaign = campaignRes.data;
      
      // Create sequence
      await axios.post(`${API}/campaigns/${newCampaign.id}/sequence`, {
        campaign_id: newCampaign.id,
        touchpoint_config: touchpointConfig,
      });
      
      setSelectedCampaign(newCampaign);
      setCurrentStep('timeline');
      toast.success('Campaign and sequence created!');
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create campaign');
    } finally {
      setLoading(false);
    }
  };

  const handleViewTimeline = async (campaign) => {
    try {
      await axios.get(`${API}/campaigns/${campaign.id}/sequence`);
      setSelectedCampaign(campaign);
      setCurrentStep('timeline');
    } catch (error) {
      toast.error('No sequence found for this campaign');
    }
  };

  const handleBackToList = () => {
    setCurrentStep('list');
    setSelectedCampaign(null);
    fetchData();
  };

  // Render Campaign List
  if (currentStep === 'list') {
    return (
      <Layout user={user} onLogout={onLogout}>
        <div className="p-8" data-testid="campaign-builder-page">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-4xl font-bold text-slate-900 mb-2">Campaign Builder</h1>
              <p className="text-slate-600">Design multi-touch outbound campaigns with AI</p>
            </div>
            <Button
              onClick={handleCreateCampaign}
              data-testid="create-campaign-button"
              className="bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 text-white shadow-lg"
            >
              <Plus size={20} className="mr-2" />
              Create Campaign
            </Button>
          </div>

          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
          ) : campaigns.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-xl border border-slate-200">
              <Megaphone className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-slate-900 mb-2">No campaigns yet</h3>
              <p className="text-slate-600">Create your first campaign to start engaging prospects</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {campaigns.map((campaign) => (
                <Card
                  key={campaign.id}
                  className="p-6 bg-white border border-slate-200 shadow-lg hover:shadow-xl transition-shadow cursor-pointer"
                  onClick={() => handleViewTimeline(campaign)}
                >
                  <h3 className="text-lg font-bold text-slate-900 mb-2">{campaign.campaign_name}</h3>
                  <div className="flex items-center gap-2 mb-3">
                    <span className="px-2 py-1 bg-indigo-100 text-indigo-700 text-xs rounded-full">{campaign.service}</span>
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">{campaign.stage}</span>
                  </div>
                  <p className="text-sm text-slate-600">ICP: {campaign.icp?.join(', ')}</p>
                  <Button variant="outline" className="w-full mt-4">
                    View Sequence <ArrowRight size={16} className="ml-2" />
                  </Button>
                </Card>
              ))}
            </div>
          )}
        </div>
      </Layout>
    );
  }

  // Render Configuration Page
  if (currentStep === 'config') {
    return (
      <Layout user={user} onLogout={onLogout}>
        <div className="p-8">
          <div className="max-w-4xl mx-auto">
            <Button variant="outline" onClick={handleBackToList} className="mb-6">
              ← Back to Campaigns
            </Button>
            
            <h1 className="text-4xl font-bold text-slate-900 mb-8">Design Your Sequence</h1>

            <form onSubmit={handleConfigSubmit} className="space-y-8">
              {/* Basic Campaign Info */}
              <Card className="p-6 bg-white">
                <h3 className="text-lg font-bold text-slate-900 mb-4">Campaign Details</h3>
                <div className="space-y-4">
                  <div>
                    <Label>Campaign Name *</Label>
                    <Input
                      value={formData.campaign_name}
                      onChange={(e) => setFormData({ ...formData, campaign_name: e.target.value })}
                      placeholder="Q1 Outreach Campaign"
                      required
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Select Agent *</Label>
                      <Select value={formData.agent_id} onValueChange={handleAgentSelect} required>
                        <SelectTrigger>
                          <SelectValue placeholder="Choose agent" />
                        </SelectTrigger>
                        <SelectContent>
                          {agents.map((agent) => (
                            <SelectItem key={agent.id} value={agent.id}>
                              {agent.agent_name} - {agent.service}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>Service *</Label>
                      <Select value={formData.service} onValueChange={(value) => setFormData({ ...formData, service: value })} required>
                        <SelectTrigger>
                          <SelectValue placeholder="Select service" />
                        </SelectTrigger>
                        <SelectContent>
                          {SERVICES.map((service) => (
                            <SelectItem key={service} value={service}>{service}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div>
                    <Label>Target ICP *</Label>
                    <Input
                      value={formData.icp}
                      onChange={(e) => setFormData({ ...formData, icp: e.target.value })}
                      placeholder="Enterprise, Mid-market, Tech companies"
                      required
                    />
                  </div>
                </div>
              </Card>

              {/* Funnel Stage Selection */}
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <Filter size={20} className="text-slate-600" />
                  <Label className="text-lg font-semibold">Select Funnel Stage</Label>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  {FUNNEL_STAGES.map((stage) => (
                    <Card
                      key={stage.value}
                      onClick={() => setFormData({ ...formData, stage: stage.value })}
                      className={`p-6 cursor-pointer transition-all ${
                        formData.stage === stage.value
                          ? 'bg-gradient-to-br from-indigo-50 to-blue-50 border-2 border-indigo-600'
                          : 'bg-white border border-slate-200 hover:border-indigo-300'
                      }`}
                    >
                      <h4 className="font-bold text-slate-900 mb-1">{stage.label}</h4>
                      <p className="text-sm text-slate-600">{stage.description}</p>
                    </Card>
                  ))}
                </div>
              </div>

              {/* Touchpoint Configuration */}
              <div>
                <Label className="text-lg font-semibold mb-4 block">Total Touchpoints</Label>
                <Input
                  type="number"
                  value={touchpointConfig.total_touchpoints}
                  onChange={(e) => {
                    const total = parseInt(e.target.value) || 0;
                    setTouchpointConfig({ ...touchpointConfig, total_touchpoints: total });
                  }}
                  min="1"
                  max="20"
                  className="max-w-xs"
                />

                <div className="grid grid-cols-3 gap-4 mt-6">
                  <Card className="p-6 bg-gradient-to-br from-blue-50 to-cyan-50 border border-blue-200">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                        <Mail className="text-white" size={20} />
                      </div>
                      <span className="font-semibold text-slate-900">Email</span>
                    </div>
                    <Input
                      type="number"
                      value={touchpointConfig.email_count}
                      onChange={(e) => setTouchpointConfig({ ...touchpointConfig, email_count: parseInt(e.target.value) || 0 })}
                      min="0"
                      className="bg-white"
                    />
                  </Card>

                  <Card className="p-6 bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center">
                        <MessageSquare className="text-white" size={20} />
                      </div>
                      <span className="font-semibold text-slate-900">LinkedIn</span>
                    </div>
                    <Input
                      type="number"
                      value={touchpointConfig.linkedin_count}
                      onChange={(e) => setTouchpointConfig({ ...touchpointConfig, linkedin_count: parseInt(e.target.value) || 0 })}
                      min="0"
                      className="bg-white"
                    />
                  </Card>

                  <Card className="p-6 bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
                        <Phone className="text-white" size={20} />
                      </div>
                      <span className="font-semibold text-slate-900">Voicemail</span>
                    </div>
                    <Input
                      type="number"
                      value={touchpointConfig.voicemail_count}
                      onChange={(e) => setTouchpointConfig({ ...touchpointConfig, voicemail_count: parseInt(e.target.value) || 0 })}
                      min="0"
                      className="bg-white"
                    />
                  </Card>
                </div>
              </div>

              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 text-white py-6 text-lg"
              >
                {loading ? 'Creating...' : 'Continue to Timeline'} <ArrowRight size={20} className="ml-2" />
              </Button>
            </form>
          </div>
        </div>
      </Layout>
    );
  }

  // Render Timeline Page
  if (currentStep === 'timeline' && selectedCampaign) {
    return (
      <CampaignTimeline
        campaign={selectedCampaign}
        user={user}
        onLogout={onLogout}
        onBack={handleBackToList}
      />
    );
  }

  return null;
};

export default CampaignBuilder;