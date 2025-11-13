import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from './Layout';
import { toast } from 'sonner';
import {
  ArrowLeft, Mail, MessageSquare, Phone, Sparkles, Copy,
  FileDown, Send, Edit2, Trash2, Save, Check, Filter,
  AlertTriangle
} from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Textarea } from './ui/textarea';
import { Card } from './ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from './ui/resizable';

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

const CampaignEditor = ({ campaign, agents, user, onLogout, onBack, editMode }) => {
  const [loading, setLoading] = useState(false);
  const [configConfirmed, setConfigConfirmed] = useState(editMode);
  const [sequence, setSequence] = useState(null);
  const [generatingStep, setGeneratingStep] = useState(null);
  const [editingStep, setEditingStep] = useState(null);
  const [editContent, setEditContent] = useState('');
  const [deleteConfirmStep, setDeleteConfirmStep] = useState(null);
  const [currentCampaign, setCurrentCampaign] = useState(campaign);
  const [deleteCampaignConfirm, setDeleteCampaignConfirm] = useState(false);

  const [formData, setFormData] = useState({
    campaign_name: campaign?.campaign_name || '',
    agent_id: campaign?.agent_id || '',
    service: campaign?.service || '',
    stage: campaign?.stage || 'TOFU',
    icp: campaign?.icp?.join(', ') || '',
    methodologies: campaign?.methodologies?.join(', ') || '',
    tone: campaign?.tone || 'professional',
    resources: campaign?.resources?.join(', ') || '',
  });

  const [touchpointConfig, setTouchpointConfig] = useState({
    total_touchpoints: 7,
    email_count: 4,
    linkedin_count: 2,
    voicemail_count: 1,
  });

  useEffect(() => {
    if (editMode && campaign) {
      fetchSequence();
    }
  }, [editMode, campaign]);

  const fetchSequence = async () => {
    if (!currentCampaign) return;
    try {
      const response = await axios.get(`${API}/campaigns/${currentCampaign.id}/sequence`);
      setSequence(response.data);
    } catch (error) {
      console.error('Failed to fetch sequence');
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

  const handleConfigConfirm = async () => {
    if (!formData.campaign_name || !formData.agent_id || !formData.service) {
      toast.error('Please fill in all required fields');
      return;
    }

    setLoading(true);
    const payload = {
      ...formData,
      icp: formData.icp.split(',').map(i => i.trim()).filter(Boolean),
      methodologies: formData.methodologies.split(',').map(m => m.trim()).filter(Boolean),
      resources: formData.resources.split(',').map(r => r.trim()).filter(Boolean),
    };

    try {
      let campaignData;
      if (editMode && currentCampaign) {
        await axios.put(`${API}/campaigns/${currentCampaign.id}`, payload);
        campaignData = { ...currentCampaign, ...payload };
        toast.success('Campaign configuration updated!');
      } else {
        const campaignRes = await axios.post(`${API}/campaigns`, payload);
        campaignData = campaignRes.data;
        setCurrentCampaign(campaignData);

        const sequenceRes = await axios.post(`${API}/campaigns/${campaignData.id}/sequence`, {
          campaign_id: campaignData.id,
          touchpoint_config: touchpointConfig,
        });
        
        // Set the sequence immediately from the response
        if (sequenceRes.data) {
          setSequence(sequenceRes.data);
        }
        toast.success('Campaign and sequence created!');
      }

      setConfigConfirmed(true);
      
      // Fetch sequence to ensure we have the latest data
      if (campaignData) {
        const response = await axios.get(`${API}/campaigns/${campaignData.id}/sequence`);
        setSequence(response.data);
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save campaign');
    } finally {
      setLoading(false);
    }
  };

  const handleEditConfig = () => setConfigConfirmed(false);
  const handleSaveAll = async () => {
    toast.success('Campaign saved successfully!');
    onBack();
  };

  const handleGenerateContent = async (stepNumber) => {
    setGeneratingStep(stepNumber);
    try {
      await axios.post(`${API}/campaigns/${currentCampaign.id}/sequence/steps/${stepNumber}/generate`);
      toast.success('Content generated!');
      await fetchSequence();
    } catch {
      toast.error('Failed to generate content');
    } finally {
      setGeneratingStep(null);
    }
  };

  const handleEditContent = (step) => {
    setEditingStep(step);
    setEditContent(step.content || '');
  };

  const handleSaveEdit = async () => {
    try {
      await axios.put(`${API}/campaigns/${currentCampaign.id}/sequence/steps/${editingStep.step_number}`, { content: editContent });
      toast.success('Content updated!');
      setEditingStep(null);
      await fetchSequence();
    } catch {
      toast.error('Failed to update content');
    }
  };

  const handleDeleteStep = async (stepNumber) => {
    try {
      await axios.delete(`${API}/campaigns/${currentCampaign.id}/sequence/steps/${stepNumber}`);
      toast.success('Step deleted!');
      setDeleteConfirmStep(null);
      await fetchSequence();
    } catch {
      toast.error('Failed to delete step');
    }
  };

  const handleDeleteCampaign = async () => {
    if (!currentCampaign) return;
    try {
      setLoading(true);
      await axios.delete(`${API}/campaigns/${currentCampaign.id}`);
      toast.success('Campaign deleted successfully!');
      setDeleteCampaignConfirm(false);
      onBack();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete campaign');
    } finally {
      setLoading(false);
    }
  };

  const getChannelIcon = (channel) => {
    switch (channel) {
      case 'email': return <Mail className="text-white" size={18} />;
      case 'linkedin': return <MessageSquare className="text-white" size={18} />;
      case 'voicemail': return <Phone className="text-white" size={18} />;
      default: return <Mail className="text-white" size={18} />;
    }
  };

  const getChannelColor = (channel) => {
    switch (channel) {
      case 'email': return 'bg-blue-600';
      case 'linkedin': return 'bg-purple-600';
      case 'voicemail': return 'bg-green-600';
      default: return 'bg-slate-600';
    }
  };

  const capitalizeFirst = (str) => str.charAt(0).toUpperCase() + str.slice(1);

  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="h-[calc(100vh-4rem)]">
        <div className="px-8 pt-6 pb-4 border-b border-slate-200 bg-white">
          <Button variant="outline" onClick={onBack} className="mb-4">
            <ArrowLeft size={16} className="mr-2" /> Back to Campaigns
          </Button>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 mb-1">
                {editMode ? 'Edit Campaign' : 'Create New Campaign'}
              </h1>
              <p className="text-slate-600">
                {editMode ? `Editing: ${campaign?.campaign_name}` : 'Design your multi-touch campaign sequence'}
              </p>
            </div>
            <div className="flex gap-2">
              {editMode && (
                <Button
                  onClick={() => setDeleteCampaignConfirm(true)}
                  disabled={loading}
                  variant="destructive"
                >
                  <Trash2 size={16} className="mr-2" /> Delete Campaign
                </Button>
              )}
              <Button
                onClick={handleSaveAll}
                disabled={!configConfirmed || loading}
                className="bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700"
              >
                <Save size={16} className="mr-2" /> Save Campaign
              </Button>
            </div>
          </div>
        </div>

        <ResizablePanelGroup direction="horizontal" className="h-[calc(100%-120px)]">

          {/* LEFT PANEL */}
          <ResizablePanel defaultSize={35} minSize={30}>
            <div className="h-full overflow-y-auto p-8 bg-slate-50">
              <div className="max-w-2xl">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-slate-900">Campaign Configuration</h2>
                  {configConfirmed && (
                    <div className="flex items-center gap-2">
                      <div className="flex items-center gap-2 text-green-600">
                        <Check size={16} />
                        <span className="text-sm font-medium">Confirmed</span>
                      </div>
                      <Button size="sm" variant="outline" onClick={handleEditConfig}>
                        <Edit2 size={14} className="mr-1" /> Edit
                      </Button>
                    </div>
                  )}
                </div>

                <div className="space-y-6">
                  {/* Campaign Details Card */}
                  <Card className="p-6 bg-white">
                    <h3 className="text-lg font-semibold text-slate-900 mb-4">Campaign Details</h3>
                    <div className="space-y-4">
                      <div>
                        <Label>Campaign Name *</Label>
                        <Input
                          value={formData.campaign_name}
                          onChange={(e) => setFormData({ ...formData, campaign_name: e.target.value })}
                          placeholder="Q1 Outreach Campaign"
                          disabled={configConfirmed}
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label>Select Agent *</Label>
                          <Select value={formData.agent_id} onValueChange={handleAgentSelect} disabled={configConfirmed}>
                            <SelectTrigger>
                              <SelectValue placeholder="Choose agent" />
                            </SelectTrigger>
                            <SelectContent>
                              {agents.map(agent => <SelectItem key={agent.id} value={agent.id}>{agent.agent_name}</SelectItem>)}
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label>Service *</Label>
                          <Select
                            value={formData.service}
                            onValueChange={(value) => setFormData({ ...formData, service: value })}
                            disabled={configConfirmed}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Select service" />
                            </SelectTrigger>
                            <SelectContent>
                              {SERVICES.map(service => <SelectItem key={service} value={service}>{service}</SelectItem>)}
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
                          disabled={configConfirmed}
                        />
                      </div>
                    </div>
                  </Card>

                  {/* Funnel Stage */}
                  <div className="grid grid-cols-3 gap-3">
                      {FUNNEL_STAGES.map(stage => (
                        <Card
                          key={stage.value}
                          onClick={() => !configConfirmed && setFormData({ ...formData, stage: stage.value })}
                          className={`p-4 cursor-pointer transition-all rounded-xl
                            ${formData.stage === stage.value
                              ? 'bg-gradient-to-br from-indigo-50 to-blue-50 border-2 border-indigo-600'
                              : 'bg-white border border-slate-200 hover:border-indigo-300'
                            }
                            ${configConfirmed ? 'cursor-not-allowed opacity-75' : ''}
                          `}
                        >
                          <h4 className="font-bold text-slate-900 text-sm mb-1">{stage.label}</h4>
                          <p className="text-xs text-slate-600">{stage.description}</p>
                        </Card>
                      ))}
                    </div>



                  {/* Touchpoint Configuration */}
                  <Card className="p-6 bg-white">
                    <Label className="text-lg font-semibold mb-4 block">Touchpoints</Label>
                    <div className="space-y-4">
                      <div>
                        <Label className="text-sm">Total Touchpoints</Label>
                        <Input
                          type="number"
                          value={touchpointConfig.total_touchpoints}
                          onChange={e => setTouchpointConfig({ ...touchpointConfig, total_touchpoints: parseInt(e.target.value) || 0 })}
                          min="1" max="20"
                          disabled={configConfirmed}
                        />
                      </div>
                      <div className="grid grid-cols-3 gap-3">
                        <div>
                          <Label className="text-xs mb-1 flex items-center gap-1">
                            <Mail size={12} className="text-blue-600" /> Email
                          </Label>
                          <Input
                            type="number"
                            value={touchpointConfig.email_count}
                            onChange={e => setTouchpointConfig({ ...touchpointConfig, email_count: parseInt(e.target.value) || 0 })}
                            min="0"
                            disabled={configConfirmed}
                          />
                        </div>
                        <div>
                          <Label className="text-xs mb-1 flex items-center gap-1">
                            <MessageSquare size={12} className="text-purple-600" /> LinkedIn
                          </Label>
                          <Input
                            type="number"
                            value={touchpointConfig.linkedin_count}
                            onChange={e => setTouchpointConfig({ ...touchpointConfig, linkedin_count: parseInt(e.target.value) || 0 })}
                            min="0"
                            disabled={configConfirmed}
                          />
                        </div>
                        <div>
                          <Label className="text-xs mb-1 flex items-center gap-1">
                            <Phone size={12} className="text-green-600" /> Voicemail
                          </Label>
                          <Input
                            type="number"
                            value={touchpointConfig.voicemail_count}
                            onChange={e => setTouchpointConfig({ ...touchpointConfig, voicemail_count: parseInt(e.target.value) || 0 })}
                            min="0"
                            disabled={configConfirmed}
                          />
                        </div>
                      </div>
                    </div>
                  </Card>

                  {/* Confirm Button */}
                  {!configConfirmed && (
                    <Button
                      onClick={handleConfigConfirm}
                      disabled={loading}
                      className="w-full bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700"
                    >
                      {loading ? 'Processing...' : 'Confirm & Build Sequence'}
                      <Check size={16} className="ml-2" />
                    </Button>
                  )}

                  {/* Configuration Summary */}
                  {configConfirmed && (
                    <Card className="p-4 bg-green-50 border-green-200">
                      <div className="flex items-start gap-2">
                        <Check size={16} className="text-green-600 mt-1" />
                        <div>
                          <p className="text-sm font-semibold text-green-900 mb-1">Configuration Confirmed</p>
                          <p className="text-xs text-green-700">
                            You can now edit, arrange, and manage your campaign sequence on the right panel.
                          </p>
                        </div>
                      </div>
                    </Card>
                  )}
                </div>
              </div>
            </div>
          </ResizablePanel>

          {/* HANDLE */}
          <ResizableHandle withHandle />

          {/* RIGHT PANEL */}
          <ResizablePanel defaultSize={65} minSize={40}>
            <div className="h-full overflow-y-auto p-8 bg-white">
              <div className="max-w-4xl mx-auto">
                {/* Sequence builder content here (full original code) */}
                                {configConfirmed ? (
                  <>
                    <h2 className="text-xl font-bold text-slate-900 mb-6">Campaign Sequence</h2>

                    {sequence?.steps?.length ? (
                      <div className="space-y-4">
                        {sequence.steps.map((step, index) => (
                          <Card key={step.step_number} className="p-4 flex justify-between items-start bg-slate-50 border border-slate-200">
                            <div className="flex items-start gap-4">
                              <div className={`w-10 h-10 flex items-center justify-center rounded-full ${getChannelColor(step.channel)}`}>
                                {getChannelIcon(step.channel)}
                              </div>
                              <div>
                                <p className="text-sm font-semibold text-slate-900 mb-1">
                                  Step {step.step_number}: {capitalizeFirst(step.channel)}
                                </p>
                                <p className="text-xs text-slate-600">
                                  {step.content || 'No content generated yet'}
                                </p>
                              </div>
                            </div>
                            <div className="flex flex-col gap-2 items-end">
                              {!step.content && (
                                <Button
                                  size="sm"
                                  onClick={() => handleGenerateContent(step.step_number)}
                                  disabled={generatingStep === step.step_number}
                                >
                                  {generatingStep === step.step_number ? 'Generating...' : 'Generate Content'}
                                </Button>
                              )}
                              {step.content && (
                                <>
                                  <Button size="sm" variant="outline" onClick={() => handleEditContent(step)}>
                                    <Edit2 size={14} className="mr-1" /> Edit
                                  </Button>
                                  <Button size="sm" variant="destructive" onClick={() => setDeleteConfirmStep(step)}>
                                    <Trash2 size={14} className="mr-1" /> Delete
                                  </Button>
                                </>
                              )}
                            </div>
                          </Card>
                        ))}
                      </div>
                    ) : (
                      <p className="text-slate-500">No steps available. Confirm configuration to build sequence.</p>
                    )}

                    {/* Edit Step Dialog */}
                    <Dialog open={!!editingStep} onOpenChange={() => setEditingStep(null)}>
                      <DialogContent className="w-[95vw] h-[90vh] max-w-none p-6 flex flex-col">
                        <DialogHeader>
                          <DialogTitle>Edit Step {editingStep?.step_number}</DialogTitle>
                          <DialogDescription>Update the content for this step.</DialogDescription>
                        </DialogHeader>

                        <div className="flex-1 mt-4">
                          <Textarea
                            value={editContent}
                            onChange={(e) => setEditContent(e.target.value)}
                            className="w-full h-full resize-none"
                          />
                        </div>

                        <div className="flex justify-end gap-2 mt-4">
                          <Button variant="outline" onClick={() => setEditingStep(null)}>Cancel</Button>
                          <Button onClick={handleSaveEdit}>Save</Button>
                        </div>
                      </DialogContent>
                    </Dialog>


                    {/* Delete Step Confirmation */}
                    <Dialog open={!!deleteConfirmStep} onOpenChange={() => setDeleteConfirmStep(null)}>
                      <DialogContent className="max-w-sm">
                        <DialogHeader>
                          <DialogTitle>Delete Step {deleteConfirmStep?.step_number}?</DialogTitle>
                          <DialogDescription>This action cannot be undone.</DialogDescription>
                        </DialogHeader>
                        <div className="flex justify-end gap-2 mt-4">
                          <Button variant="outline" onClick={() => setDeleteConfirmStep(null)}>Cancel</Button>
                          <Button variant="destructive" onClick={() => handleDeleteStep(deleteConfirmStep.step_number)}>Delete</Button>
                        </div>
                      </DialogContent>
                    </Dialog>

                    {/* Delete Campaign Confirmation */}
                    <Dialog open={deleteCampaignConfirm} onOpenChange={() => setDeleteCampaignConfirm(false)}>
                      <DialogContent className="max-w-sm">
                        <DialogHeader>
                          <DialogTitle>Delete Campaign?</DialogTitle>
                          <DialogDescription>Deleting this campaign will remove all steps and content permanently.</DialogDescription>
                        </DialogHeader>
                        <div className="flex justify-end gap-2 mt-4">
                          <Button variant="outline" onClick={() => setDeleteCampaignConfirm(false)}>Cancel</Button>
                          <Button variant="destructive" onClick={handleDeleteCampaign}>Delete Campaign</Button>
                        </div>
                      </DialogContent>
                    </Dialog>
                  </>
                ) : (
                  <p className="text-slate-500">
                    Confirm your campaign configuration on the left panel to build the sequence here.
                  </p>
                )}
              </div>
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    </Layout>
  );
};

export default CampaignEditor;

