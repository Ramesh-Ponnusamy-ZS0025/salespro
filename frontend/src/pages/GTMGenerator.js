import React, { useState } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { toast } from 'sonner';
import { Sparkles, Globe, Copy } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Card } from '../components/ui/card';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const GTMGenerator = ({ user, onLogout }) => {
  const [loading, setLoading] = useState(false);
  const [generatedPrompt, setGeneratedPrompt] = useState(null);
  const [formData, setFormData] = useState({
    company_name: '',
    linkedin_url: '',
    offering: '',
    pain_points: '',
    personas: '',
  });

  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);

    const payload = {
      ...formData,
      pain_points: formData.pain_points.split(',').map(p => p.trim()).filter(Boolean),
      personas: formData.personas.split(',').map(p => p.trim()).filter(Boolean),
      target_persons: formData.personas.split(',').map(p => p.trim()).filter(Boolean),
    };

    try {
      const response = await axios.post(`${API}/gtm/generate-prompt`, payload);
      setGeneratedPrompt(response.data);
      toast.success('GTM prompt generated successfully!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to generate prompt');
    } finally {
      setLoading(false);
    }
  };

  const copyPrompt = () => {
    if (generatedPrompt) {
      navigator.clipboard.writeText(generatedPrompt.prompt);
      toast.success('Prompt copied to clipboard!');
    }
  };

  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="p-8" data-testid="gtm-generator-page">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-slate-900 mb-2">GTM Generator</h1>
            <p className="text-slate-600">Generate prospect-specific microsite prompts for Lovable/Emergent</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-6 bg-white border border-slate-200 shadow-lg">
              <h3 className="text-lg font-bold text-slate-900 mb-4">Prospect Information</h3>
              <form onSubmit={handleGenerate} className="space-y-4">
                <div>
                  <Label>Company Name *</Label>
                  <Input
                    data-testid="company-name-input"
                    value={formData.company_name}
                    onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                    placeholder="Acme Corporation"
                    required
                  />
                </div>
                <div>
                  <Label>LinkedIn URL</Label>
                  <Input
                    value={formData.linkedin_url}
                    onChange={(e) => setFormData({ ...formData, linkedin_url: e.target.value })}
                    placeholder="https://linkedin.com/company/acme"
                  />
                </div>
                <div>
                  <Label>Your Offering *</Label>
                  <Textarea
                    data-testid="offering-input"
                    value={formData.offering}
                    onChange={(e) => setFormData({ ...formData, offering: e.target.value })}
                    placeholder="AI-powered sales automation platform that helps teams close deals faster"
                    rows={3}
                    required
                  />
                </div>
                <div>
                  <Label>Pain Points (comma-separated) *</Label>
                  <Textarea
                    value={formData.pain_points}
                    onChange={(e) => setFormData({ ...formData, pain_points: e.target.value })}
                    placeholder="Manual data entry, Low conversion rates, Inefficient follow-ups"
                    rows={2}
                    required
                  />
                </div>
                <div>
                  <Label>Target Decision Makers (comma-separated) *</Label>
                  <Input
                    data-testid="personas-input"
                    value={formData.personas}
                    onChange={(e) => setFormData({ ...formData, personas: e.target.value })}
                    placeholder="John Smith (CEO), Jane Doe (CRO), Sales Directors"
                    required
                  />
                </div>
                <Button
                  type="submit"
                  disabled={loading}
                  data-testid="generate-prompt-button"
                  className="w-full"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles size={18} className="mr-2" />
                      Generate Microsite Prompt
                    </>
                  )}
                </Button>
              </form>
            </Card>

            <div className="space-y-6">
              {generatedPrompt ? (
                <Card className="p-6 bg-white border border-slate-200 shadow-lg">
                  <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
                    <Globe className="text-indigo-600" />
                    Generated Microsite Prompt
                  </h3>
                  <div className="space-y-4">
                    <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 max-h-[500px] overflow-y-auto">
                      <p className="text-sm text-slate-800 whitespace-pre-wrap" data-testid="generated-prompt">
                        {generatedPrompt.prompt}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button onClick={copyPrompt} data-testid="copy-prompt-button" className="flex-1">
                        <Copy size={16} className="mr-2" />
                        Copy Prompt
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => window.open('https://lovable.dev', '_blank')}
                        className="flex-1"
                      >
                        Open Lovable
                      </Button>
                    </div>
                  </div>
                </Card>
              ) : (
                <Card className="p-6 bg-white border border-slate-200 shadow-lg">
                  <div className="flex flex-col items-center justify-center h-[500px] text-center">
                    <Globe className="w-20 h-20 text-slate-300 mb-4" />
                    <h3 className="text-xl font-semibold text-slate-900 mb-2">No Prompt Generated Yet</h3>
                    <p className="text-slate-600 max-w-sm">
                      Fill out the prospect information and generate a personalized microsite prompt
                    </p>
                  </div>
                </Card>
              )}

              <Card className="p-6 bg-gradient-to-br from-indigo-50 to-purple-50 border border-indigo-100">
                <h3 className="text-sm font-bold text-indigo-900 mb-3">What is GTM Generator?</h3>
                <p className="text-xs text-indigo-700 leading-relaxed">
                  The GTM (Go-To-Market) Generator creates detailed prompts for building prospect-specific microsites.
                  These prompts can be used with platforms like Lovable or Emergent to generate tailored landing pages
                  that speak directly to your prospect's needs and pain points.
                </p>
                <div className="mt-4 p-3 bg-white/60 rounded-lg">
                  <p className="text-xs font-semibold text-indigo-900 mb-1">Next Steps:</p>
                  <ol className="text-xs text-indigo-700 space-y-1 list-decimal list-inside">
                    <li>Copy the generated prompt</li>
                    <li>Open Lovable or Emergent</li>
                    <li>Paste the prompt to create microsite</li>
                    <li>Share the link with your prospect</li>
                  </ol>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default GTMGenerator;