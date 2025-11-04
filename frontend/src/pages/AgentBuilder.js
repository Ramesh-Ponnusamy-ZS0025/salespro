import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { toast } from 'sonner';
import { Plus, Edit, Trash2, Eye, Sparkles, X } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Predefined service options
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

const SUB_SERVICES = {
  'Quality Engineering': ['Test Automation', 'Performance Testing', 'Security Testing', 'Manual Testing', 'QA Consulting'],
  'Digital Transformation': ['Cloud Migration', 'Legacy Modernization', 'Digital Strategy', 'Process Automation'],
  'Data Engineering': ['Data Warehousing', 'ETL Pipeline', 'Big Data', 'Data Analytics', 'Business Intelligence'],
  'Cloud Services': ['AWS', 'Azure', 'Google Cloud', 'Multi-Cloud', 'Cloud Architecture'],
  'DevOps': ['CI/CD', 'Infrastructure as Code', 'Monitoring', 'Container Orchestration', 'Release Management'],
  'Cybersecurity': ['Security Assessment', 'Penetration Testing', 'Compliance', 'Security Operations'],
  'AI & Machine Learning': ['Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision', 'MLOps'],
  'Product Engineering': ['Product Development', 'MVP Development', 'Product Strategy', 'UX/UI Design'],
  'Consulting': ['Technology Consulting', 'Business Consulting', 'Strategy Consulting'],
};

const PERSONAS = [
  'CTO',
  'VP Engineering',
  'IT Director',
  'Head of QA',
  'DevOps Manager',
  'Product Manager',
  'Engineering Manager',
  'Director of IT',
  'Chief Digital Officer',
  'Head of Innovation',
  'Technical Architect',
  'VP of Operations',
];

const AgentBuilder = ({ user, onLogout }) => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showDialog, setShowDialog] = useState(false);
  const [editingAgent, setEditingAgent] = useState(null);
  const [preview, setPreview] = useState(null);
  const [selectedPersonas, setSelectedPersonas] = useState([]);
  const [formData, setFormData] = useState({
    agent_name: '',
    service: '',
    sub_service: '',
    value_props: '',
    pain_points: '',
    tone: 'professional',
    methodologies: '',
    example_copies: '',
  });

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await axios.get(`${API}/agents`);
      setAgents(response.data);
    } catch (error) {
      toast.error('Failed to fetch agents');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const payload = {
      ...formData,
      value_props: formData.value_props.split(',').map(v => v.trim()).filter(Boolean),
      pain_points: formData.pain_points.split(',').map(p => p.trim()).filter(Boolean),
      personas: formData.personas.split(',').map(p => p.trim()).filter(Boolean),
      methodologies: formData.methodologies.split(',').map(m => m.trim()).filter(Boolean),
      example_copies: formData.example_copies.split('\n').filter(Boolean),
    };

    try {
      if (editingAgent) {
        await axios.put(`${API}/agents/${editingAgent.id}`, payload);
        toast.success('Agent updated successfully!');
      } else {
        await axios.post(`${API}/agents`, payload);
        toast.success('Agent created successfully!');
      }
      setShowDialog(false);
      setEditingAgent(null);
      resetForm();
      fetchAgents();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save agent');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (agent) => {
    setEditingAgent(agent);
    setFormData({
      agent_name: agent.agent_name,
      service: agent.service,
      sub_service: agent.sub_service || '',
      value_props: agent.value_props.join(', '),
      pain_points: agent.pain_points.join(', '),
      personas: agent.personas.join(', '),
      tone: agent.tone,
      methodologies: agent.methodologies.join(', '),
      example_copies: agent.example_copies.join('\n'),
    });
    setShowDialog(true);
  };

  const handleDelete = async (agentId) => {
    if (!window.confirm('Are you sure you want to delete this agent?')) return;

    try {
      await axios.delete(`${API}/agents/${agentId}`);
      toast.success('Agent deleted successfully!');
      fetchAgents();
    } catch (error) {
      toast.error('Failed to delete agent');
    }
  };

  const handlePreview = async (agentId) => {
    try {
      const response = await axios.get(`${API}/agents/${agentId}/preview`);
      setPreview(response.data.preview);
    } catch (error) {
      toast.error('Failed to generate preview');
    }
  };

  const resetForm = () => {
    setFormData({
      agent_name: '',
      service: '',
      sub_service: '',
      value_props: '',
      pain_points: '',
      personas: '',
      tone: 'professional',
      methodologies: '',
      example_copies: '',
    });
  };

  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="p-8" data-testid="agent-builder-page">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-slate-900 mb-2">Agent Builder</h1>
            <p className="text-slate-600">Create and manage AI-powered sales agents</p>
          </div>
          <Dialog open={showDialog} onOpenChange={setShowDialog}>
            <DialogTrigger asChild>
              <Button
                onClick={() => {
                  setEditingAgent(null);
                  resetForm();
                }}
                data-testid="create-agent-button"
                className="bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 text-white shadow-lg"
              >
                <Plus size={20} className="mr-2" />
                Create Agent
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>{editingAgent ? 'Edit Agent' : 'Create New Agent'}</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Label>Agent Name *</Label>
                  <Input
                    data-testid="agent-name-input"
                    value={formData.agent_name}
                    onChange={(e) => setFormData({ ...formData, agent_name: e.target.value })}
                    placeholder="e.g., Digital Services Agent"
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Service *</Label>
                    <Input
                      data-testid="service-input"
                      value={formData.service}
                      onChange={(e) => setFormData({ ...formData, service: e.target.value })}
                      placeholder="e.g., Digital Transformation"
                      required
                    />
                  </div>
                  <div>
                    <Label>Sub-Service</Label>
                    <Input
                      value={formData.sub_service}
                      onChange={(e) => setFormData({ ...formData, sub_service: e.target.value })}
                      placeholder="e.g., Cloud Migration"
                    />
                  </div>
                </div>
                <div>
                  <Label>Value Propositions (comma-separated) *</Label>
                  <Textarea
                    data-testid="value-props-input"
                    value={formData.value_props}
                    onChange={(e) => setFormData({ ...formData, value_props: e.target.value })}
                    placeholder="Reduce costs by 40%, Improve efficiency, Scale operations"
                    required
                  />
                </div>
                <div>
                  <Label>Pain Points (comma-separated) *</Label>
                  <Textarea
                    value={formData.pain_points}
                    onChange={(e) => setFormData({ ...formData, pain_points: e.target.value })}
                    placeholder="Legacy systems, Manual processes, Limited scalability"
                    required
                  />
                </div>
                <div>
                  <Label>Target Personas (comma-separated) *</Label>
                  <Input
                    value={formData.personas}
                    onChange={(e) => setFormData({ ...formData, personas: e.target.value })}
                    placeholder="CTO, VP Engineering, IT Director"
                    required
                  />
                </div>
                <div>
                  <Label>Tone *</Label>
                  <Select value={formData.tone} onValueChange={(value) => setFormData({ ...formData, tone: value })}>
                    <SelectTrigger data-testid="tone-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="professional">Professional</SelectItem>
                      <SelectItem value="casual">Casual</SelectItem>
                      <SelectItem value="friendly">Friendly</SelectItem>
                      <SelectItem value="authoritative">Authoritative</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Methodologies (comma-separated)</Label>
                  <Input
                    value={formData.methodologies}
                    onChange={(e) => setFormData({ ...formData, methodologies: e.target.value })}
                    placeholder="KISS, GAP, StoryBrand, PAS"
                  />
                </div>
                <div className="flex gap-2 pt-4">
                  <Button type="submit" disabled={loading} data-testid="save-agent-button" className="flex-1">
                    {loading ? 'Saving...' : editingAgent ? 'Update Agent' : 'Create Agent'}
                  </Button>
                  <Button type="button" variant="outline" onClick={() => setShowDialog(false)}>
                    Cancel
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {loading && agents.length === 0 ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        ) : agents.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-xl border border-slate-200">
            <Sparkles className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-900 mb-2">No agents yet</h3>
            <p className="text-slate-600 mb-6">Create your first AI sales agent to get started</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {agents.map((agent) => (
              <div
                key={agent.id}
                data-testid={`agent-card-${agent.id}`}
                className="bg-white rounded-xl p-6 shadow-lg border border-slate-200 hover:shadow-xl transition-all duration-200"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-slate-900 mb-1">{agent.agent_name}</h3>
                    <p className="text-sm text-slate-600">{agent.service}</p>
                  </div>
                  <Badge className="bg-indigo-100 text-indigo-700 hover:bg-indigo-200">
                    v{agent.version}
                  </Badge>
                </div>
                <div className="space-y-2 mb-4">
                  <div>
                    <p className="text-xs font-semibold text-slate-700 mb-1">Tone:</p>
                    <Badge variant="outline">{agent.tone}</Badge>
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-slate-700 mb-1">Value Props:</p>
                    <p className="text-xs text-slate-600">{agent.value_props.slice(0, 2).join(', ')}</p>
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-slate-700 mb-1">Usage:</p>
                    <p className="text-xs text-slate-600">{agent.usage_count} campaigns</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handlePreview(agent.id)}
                    data-testid={`preview-agent-${agent.id}`}
                    className="flex-1"
                  >
                    <Eye size={16} className="mr-1" />
                    Preview
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleEdit(agent)}
                    data-testid={`edit-agent-${agent.id}`}
                  >
                    <Edit size={16} />
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleDelete(agent.id)}
                    data-testid={`delete-agent-${agent.id}`}
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 size={16} />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Preview Modal */}
        {preview && (
          <Dialog open={!!preview} onOpenChange={() => setPreview(null)}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Agent Preview</DialogTitle>
              </DialogHeader>
              <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                <p className="text-slate-800 whitespace-pre-wrap">{preview}</p>
              </div>
            </DialogContent>
          </Dialog>
        )}
      </div>
    </Layout>
  );
};

export default AgentBuilder;
