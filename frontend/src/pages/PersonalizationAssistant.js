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
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PersonalizationAssistant = ({ user, onLogout }) => {
  const [agents, setAgents] = useState([]);
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generatedMessage, setGeneratedMessage] = useState(null);
  const [showProfileDialog, setShowProfileDialog] = useState(false);
  const [formData, setFormData] = useState({
    origin_url: '',
    agent_id: '',
    sender_profile_id: '',
    keywords: '',
    notes: '',
  });
  const [profileForm, setProfileForm] = useState({
    name: '',
    position: '',
    company: '',
    email: '',
    phone: '',
    signature_template: '',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [agentsRes, profilesRes] = await Promise.all([
        axios.get(`${API}/agents`),
        axios.get(`${API}/sender-profiles`),
      ]);
      setAgents(agentsRes.data);
      setProfiles(profilesRes.data);
    } catch (error) {
      toast.error('Failed to fetch data');
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);

    const payload = {
      ...formData,
      keywords: formData.keywords.split(',').map(k => k.trim()).filter(Boolean),
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

  const handleCreateProfile = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/sender-profiles`, profileForm);
      toast.success('Sender profile created!');
      setShowProfileDialog(false);
      setProfileForm({
        name: '',
        position: '',
        company: '',
        email: '',
        phone: '',
        signature_template: '',
      });
      fetchData();
    } catch (error) {
      toast.error('Failed to create profile');
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
                  <Label>Sender Profile *</Label>
                  <div className="flex gap-2">
                    <Select
                      value={formData.sender_profile_id}
                      onValueChange={(value) => setFormData({ ...formData, sender_profile_id: value })}
                      required
                    >
                      <SelectTrigger data-testid="profile-select" className="flex-1">
                        <SelectValue placeholder="Choose a profile" />
                      </SelectTrigger>
                      <SelectContent>
                        {profiles.map((profile) => (
                          <SelectItem key={profile.id} value={profile.id}>
                            {profile.name} - {profile.position}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Dialog open={showProfileDialog} onOpenChange={setShowProfileDialog}>
                      <DialogTrigger asChild>
                        <Button type="button" variant="outline" size="icon" data-testid="add-profile-button">
                          <User size={18} />
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Create Sender Profile</DialogTitle>
                        </DialogHeader>
                        <form onSubmit={handleCreateProfile} className="space-y-3">
                          <div>
                            <Label>Name *</Label>
                            <Input
                              value={profileForm.name}
                              onChange={(e) => setProfileForm({ ...profileForm, name: e.target.value })}
                              required
                            />
                          </div>
                          <div>
                            <Label>Position *</Label>
                            <Input
                              value={profileForm.position}
                              onChange={(e) => setProfileForm({ ...profileForm, position: e.target.value })}
                              required
                            />
                          </div>
                          <div>
                            <Label>Company *</Label>
                            <Input
                              value={profileForm.company}
                              onChange={(e) => setProfileForm({ ...profileForm, company: e.target.value })}
                              required
                            />
                          </div>
                          <div>
                            <Label>Email *</Label>
                            <Input
                              type="email"
                              value={profileForm.email}
                              onChange={(e) => setProfileForm({ ...profileForm, email: e.target.value })}
                              required
                            />
                          </div>
                          <div>
                            <Label>Phone</Label>
                            <Input
                              value={profileForm.phone}
                              onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })}
                            />
                          </div>
                          <div>
                            <Label>Signature Template *</Label>
                            <Textarea
                              value={profileForm.signature_template}
                              onChange={(e) => setProfileForm({ ...profileForm, signature_template: e.target.value })}
                              placeholder="Best regards,\n{name}\n{position}\n{company}"
                              required
                            />
                          </div>
                          <Button type="submit" className="w-full">Create Profile</Button>
                        </form>
                      </DialogContent>
                    </Dialog>
                  </div>
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
                  <Label>Additional Notes</Label>
                  <Textarea
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
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
