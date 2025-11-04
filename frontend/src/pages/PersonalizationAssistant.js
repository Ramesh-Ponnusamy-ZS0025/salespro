import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { toast } from 'sonner';
import { Sparkles, Copy, User } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Card } from '../components/ui/card';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PersonalizationAssistant = ({ user, onLogout }) => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generatedMessage, setGeneratedMessage] = useState(null);
  const [userProfile, setUserProfile] = useState({
    name: user?.username || '',
    position: '',
    company: '',
    email: user?.email || '',
    phone: '',
  });
  const [formData, setFormData] = useState({
    origin_url: '',
    agent_id: '',
    keywords: '',
    custom_input: '',
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
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);

    const payload = {
      origin_url: formData.origin_url,
      agent_id: formData.agent_id,
      keywords: formData.keywords.split(',').map(k => k.trim()).filter(Boolean),
      notes: formData.custom_input,
      sender_profile: userProfile,
    };

    try {
      const response = await axios.post(`${API}/personalize/generate`, payload);
      setGeneratedMessage(response.data);
      toast.success('Personalized message generated!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to generate message');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (generatedMessage) {
      navigator.clipboard.writeText(generatedMessage.message);
      toast.success('Copied to clipboard!');
    }
  };

  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="p-8" data-testid="personalization-assistant-page">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-slate-900 mb-2">Personalization Assistant</h1>
            <p className="text-slate-600">Generate personalized 1:1 messages for prospects</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-6 bg-white border border-slate-200 shadow-lg">
              <h3 className="text-lg font-bold text-slate-900 mb-4">Generate Message</h3>
              
              {/* User Profile Section */}
              <div className="mb-6 p-4 bg-indigo-50 rounded-lg border border-indigo-200">
                <div className="flex items-center gap-2 mb-3">
                  <User size={18} className="text-indigo-600" />
                  <Label className="text-indigo-900 font-semibold">Your Profile (Editable)</Label>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <Input
                    placeholder="Name"
                    value={userProfile.name}
                    onChange={(e) => setUserProfile({ ...userProfile, name: e.target.value })}
                    className="bg-white"
                  />
                  <Input
                    placeholder="Position"
                    value={userProfile.position}
                    onChange={(e) => setUserProfile({ ...userProfile, position: e.target.value })}
                    className="bg-white"
                  />
                  <Input
                    placeholder="Company"
                    value={userProfile.company}
                    onChange={(e) => setUserProfile({ ...userProfile, company: e.target.value })}
                    className="bg-white"
                  />
                  <Input
                    placeholder="Email"
                    value={userProfile.email}
                    onChange={(e) => setUserProfile({ ...userProfile, email: e.target.value })}
                    className="bg-white"
                  />
                  <Input
                    placeholder="Phone"
                    value={userProfile.phone}
                    onChange={(e) => setUserProfile({ ...userProfile, phone: e.target.value })}
                    className="bg-white col-span-2"
                  />
                </div>
              </div>

              <form onSubmit={handleGenerate} className="space-y-4">
                <div>
                  <Label>LinkedIn or Company URL *</Label>
                  <Input
                    data-testid="origin-url-input"
                    value={formData.origin_url}
                    onChange={(e) => setFormData({ ...formData, origin_url: e.target.value })}
                    placeholder="https://linkedin.com/in/..."
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
                <div>
                  <Label>Keywords (comma-separated)</Label>
                  <Input
                    value={formData.keywords}
                    onChange={(e) => setFormData({ ...formData, keywords: e.target.value })}
                    placeholder="innovation, growth, transformation"
                  />
                </div>
                <div>
                  <Label>Custom Input</Label>
                  <Textarea
                    value={formData.custom_input}
                    onChange={(e) => setFormData({ ...formData, custom_input: e.target.value })}
                    placeholder="Any specific context or details..."
                    rows={3}
                  />
                </div>
                <Button type="submit" disabled={loading} data-testid="generate-message-button" className="w-full">
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles size={18} className="mr-2" />
                      Generate Message
                    </>
                  )}
                </Button>
              </form>
            </Card>

            <Card className="p-6 bg-white border border-slate-200 shadow-lg">
              <h3 className="text-lg font-bold text-slate-900 mb-4">Generated Message</h3>
              {generatedMessage ? (
                <div className="space-y-4">
                  <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 min-h-[300px]">
                    <p className="text-slate-800 whitespace-pre-wrap" data-testid="generated-message">
                      {generatedMessage.message}
                    </p>
                  </div>
                  <div className="flex items-center justify-between">
                    <p className="text-sm text-slate-600">
                      Character count: <span className="font-semibold">{generatedMessage.char_count}</span>/500
                    </p>
                    <Button onClick={copyToClipboard} data-testid="copy-message-button" variant="outline">
                      <Copy size={16} className="mr-2" />
                      Copy
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-[350px] text-center">
                  <Sparkles className="w-16 h-16 text-slate-300 mb-4" />
                  <p className="text-slate-600">Your personalized message will appear here</p>
                </div>
              )}
            </Card>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default PersonalizationAssistant;