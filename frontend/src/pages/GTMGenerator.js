import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { toast } from 'sonner';
import { 
  Sparkles, Globe, Copy, Send, CheckCircle, XCircle, 
  AlertCircle, FileText, Upload, Lightbulb, RefreshCw,
  Download, ArrowRight
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const INDUSTRIES = [
  'Fintech', 'Healthcare', 'E-commerce', 'SaaS', 'Manufacturing',
  'Real Estate', 'Education', 'Retail', 'Logistics', 'Other'
];

const GTMGenerator = ({ user, onLogout }) => {
  const [step, setStep] = useState('input'); // input, validation, review, final
  const [loading, setLoading] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  const [finalPrompt, setFinalPrompt] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [userFeedback, setUserFeedback] = useState('');
  const chatEndRef = useRef(null);

  const [formData, setFormData] = useState({
    company_name: '',
    industry: '',
    linkedin_url: '',
    offering: '',
    pain_points: '',
    target_personas: '',
    use_cases: '',
    key_features: '',
  });

  const [files, setFiles] = useState([]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const addChatMessage = (message, type = 'system') => {
    setChatMessages(prev => [...prev, { message, type, timestamp: new Date() }]);
  };

  const handleValidate = async () => {
    if (!formData.company_name || !formData.industry || !formData.offering || !formData.pain_points) {
      toast.error('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setStep('validation');
    addChatMessage('🔍 Starting validation process...', 'system');

    try {
      const response = await axios.post(`${API}/gtm/validate`, {
        ...formData,
        pain_points: formData.pain_points.split(',').map(p => p.trim()).filter(Boolean),
        target_personas: formData.target_personas.split(',').map(p => p.trim()).filter(Boolean),
        use_cases: formData.use_cases.split(',').map(p => p.trim()).filter(Boolean),
        key_features: formData.key_features.split(',').map(p => p.trim()).filter(Boolean),
      });

      setValidationResult(response.data);
      
      // Add validation messages
      addChatMessage(`✅ Company: ${formData.company_name}`, 'system');
      addChatMessage(`🏢 Industry: ${formData.industry}`, 'system');
      
      if (response.data.has_use_cases) {
        addChatMessage(`📚 Found ${response.data.use_case_count} relevant use cases for ${formData.industry}`, 'success');
      } else {
        addChatMessage(`⚠️ No specific use cases found for ${formData.industry}. Will use general best practices.`, 'warning');
      }

      if (response.data.validation_notes?.length > 0) {
        response.data.validation_notes.forEach(note => {
          addChatMessage(`💡 ${note}`, 'info');
        });
      }

      addChatMessage('✨ Validation complete! Review the summary below.', 'success');
      setStep('review');

    } catch (error) {
      toast.error(error.response?.data?.detail || 'Validation failed');
      addChatMessage('❌ Validation failed. Please check your inputs.', 'error');
      setStep('input');
    } finally {
      setLoading(false);
    }
  };

  const handleUserFeedbackSubmit = async () => {
    if (!userFeedback.trim()) return;

    addChatMessage(userFeedback, 'user');
    const feedback = userFeedback;
    setUserFeedback('');
    setLoading(true);

    try {
      const response = await axios.post(`${API}/gtm/process-feedback`, {
        feedback,
        validation_result: validationResult,
        form_data: formData,
      });

      if (response.data.action === 'regenerate') {
        addChatMessage('🔄 Understood! Let me adjust the approach...', 'system');
        setValidationResult(response.data.updated_validation);
        addChatMessage(response.data.message, 'system');
      } else if (response.data.action === 'clarify') {
        addChatMessage(response.data.message, 'system');
      } else {
        addChatMessage(response.data.message, 'system');
      }
    } catch (error) {
      addChatMessage('Sorry, I had trouble processing that. Can you try rephrasing?', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateFinalPrompt = async () => {
    setLoading(true);
    addChatMessage('🚀 Generating your final microsite prompt...', 'system');

    try {
      const response = await axios.post(`${API}/gtm/generate-final-prompt`, {
        form_data: formData,
        validation_result: validationResult,
      });

      setFinalPrompt(response.data);
      addChatMessage('✅ Prompt generated successfully! You can now copy it and use it in Lovable/Emergent.', 'success');
      setStep('final');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to generate prompt');
      addChatMessage('❌ Failed to generate prompt. Please try again.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const copyPrompt = () => {
    if (finalPrompt) {
      navigator.clipboard.writeText(finalPrompt.prompt);
      toast.success('Prompt copied to clipboard!');
    }
  };

  const handleReset = () => {
    setStep('input');
    setValidationResult(null);
    setFinalPrompt(null);
    setChatMessages([]);
    setFormData({
      company_name: '',
      industry: '',
      linkedin_url: '',
      offering: '',
      pain_points: '',
      target_personas: '',
      use_cases: '',
      key_features: '',
    });
    setFiles([]);
  };

  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8 text-center">
            <div className="flex items-center justify-center gap-3 mb-3">
              <Globe className="w-12 h-12 text-indigo-600" />
              <h1 className="text-5xl font-bold text-slate-900">GTM Microsite Generator</h1>
            </div>
            <p className="text-lg text-slate-600">
              Generate validated, prospect-specific microsite prompts powered by AI
            </p>
          </div>

          {/* Progress Steps */}
          <div className="mb-8">
            <div className="flex items-center justify-center gap-4">
              <StepIndicator active={step === 'input'} completed={['validation', 'review', 'final'].includes(step)} label="Input Details" />
              <div className="w-16 h-1 bg-slate-200" />
              <StepIndicator active={step === 'validation'} completed={['review', 'final'].includes(step)} label="Validation" />
              <div className="w-16 h-1 bg-slate-200" />
              <StepIndicator active={step === 'review'} completed={step === 'final'} label="Review" />
              <div className="w-16 h-1 bg-slate-200" />
              <StepIndicator active={step === 'final'} label="Final Prompt" />
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Panel - Input Form */}
            <div className="lg:col-span-2">
              <Card className="p-6 bg-white shadow-xl border-2 border-slate-200">
                {step === 'input' && (
                  <>
                    <h2 className="text-2xl font-bold text-slate-900 mb-6">Prospect Information</h2>
                    <div className="space-y-5">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label className="text-sm font-semibold">Company Name *</Label>
                          <Input
                            value={formData.company_name}
                            onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                            placeholder="Acme Corporation"
                            className="mt-1"
                          />
                        </div>
                        <div>
                          <Label className="text-sm font-semibold">Industry *</Label>
                          <select
                            value={formData.industry}
                            onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                            className="mt-1 w-full border border-slate-300 rounded-md px-3 py-2 text-sm"
                          >
                            <option value="">Select Industry</option>
                            {INDUSTRIES.map(ind => <option key={ind} value={ind}>{ind}</option>)}
                          </select>
                        </div>
                      </div>

                      <div>
                        <Label className="text-sm font-semibold">LinkedIn URL</Label>
                        <Input
                          value={formData.linkedin_url}
                          onChange={(e) => setFormData({ ...formData, linkedin_url: e.target.value })}
                          placeholder="https://linkedin.com/company/acme"
                          className="mt-1"
                        />
                      </div>

                      <div>
                        <Label className="text-sm font-semibold">Your Offering *</Label>
                        <Textarea
                          value={formData.offering}
                          onChange={(e) => setFormData({ ...formData, offering: e.target.value })}
                          placeholder="AI-powered sales automation platform that helps teams close deals faster..."
                          rows={3}
                          className="mt-1"
                        />
                      </div>

                      <div>
                        <Label className="text-sm font-semibold">Pain Points (comma-separated) *</Label>
                        <Textarea
                          value={formData.pain_points}
                          onChange={(e) => setFormData({ ...formData, pain_points: e.target.value })}
                          placeholder="Manual data entry, Low conversion rates, Inefficient follow-ups"
                          rows={2}
                          className="mt-1"
                        />
                      </div>

                      <div>
                        <Label className="text-sm font-semibold">Target Decision Makers (comma-separated) *</Label>
                        <Input
                          value={formData.target_personas}
                          onChange={(e) => setFormData({ ...formData, target_personas: e.target.value })}
                          placeholder="John Smith (CEO), Jane Doe (CRO), Sales Directors"
                          className="mt-1"
                        />
                      </div>

                      <div>
                        <Label className="text-sm font-semibold">Use Cases (comma-separated)</Label>
                        <Textarea
                          value={formData.use_cases}
                          onChange={(e) => setFormData({ ...formData, use_cases: e.target.value })}
                          placeholder="Lead scoring automation, Email campaign optimization, CRM integration"
                          rows={2}
                          className="mt-1"
                        />
                      </div>

                      <div>
                        <Label className="text-sm font-semibold">Key Features (comma-separated)</Label>
                        <Input
                          value={formData.key_features}
                          onChange={(e) => setFormData({ ...formData, key_features: e.target.value })}
                          placeholder="AI predictions, Real-time analytics, Integrations"
                          className="mt-1"
                        />
                      </div>

                      <div>
                        <Label className="text-sm font-semibold">Upload Screenshots/Use Cases (Optional)</Label>
                        <div className="mt-2 border-2 border-dashed border-slate-300 rounded-lg p-4 text-center hover:border-indigo-400 transition cursor-pointer">
                          <Upload className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                          <p className="text-sm text-slate-600">Click to upload or drag and drop</p>
                          <p className="text-xs text-slate-500 mt-1">PNG, JPG, PDF up to 10MB</p>
                        </div>
                      </div>

                      <Button
                        onClick={handleValidate}
                        disabled={loading}
                        className="w-full bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 text-lg py-6"
                      >
                        {loading ? 'Validating...' : (
                          <>
                            <Sparkles size={20} className="mr-2" />
                            Validate & Generate Prompt
                          </>
                        )}
                      </Button>
                    </div>
                  </>
                )}

                {(step === 'validation' || step === 'review') && (
                  <>
                    <h2 className="text-2xl font-bold text-slate-900 mb-6">Validation Summary</h2>
                    
                    {validationResult && (
                      <div className="space-y-4">
                        <Card className="p-4 bg-blue-50 border-blue-200">
                          <h3 className="font-semibold text-blue-900 mb-2">Company Profile</h3>
                          <p className="text-sm text-blue-800">
                            <strong>{formData.company_name}</strong> • {formData.industry}
                          </p>
                        </Card>

                        <Card className="p-4 bg-green-50 border-green-200">
                          <h3 className="font-semibold text-green-900 mb-2">Data Availability</h3>
                          <div className="space-y-2">
                            <div className="flex items-center gap-2">
                              {validationResult.has_use_cases ? (
                                <CheckCircle className="w-4 h-4 text-green-600" />
                              ) : (
                                <AlertCircle className="w-4 h-4 text-yellow-600" />
                              )}
                              <span className="text-sm">
                                {validationResult.has_use_cases 
                                  ? `${validationResult.use_case_count} use cases available`
                                  : 'No specific use cases (will use general best practices)'}
                              </span>
                            </div>
                            <div className="flex items-center gap-2">
                              <CheckCircle className="w-4 h-4 text-green-600" />
                              <span className="text-sm">Industry patterns validated</span>
                            </div>
                          </div>
                        </Card>

                        {validationResult.suggestions?.length > 0 && (
                          <Card className="p-4 bg-purple-50 border-purple-200">
                            <h3 className="font-semibold text-purple-900 mb-2 flex items-center gap-2">
                              <Lightbulb className="w-4 h-4" />
                              Suggestions
                            </h3>
                            <ul className="space-y-1">
                              {validationResult.suggestions.map((sug, idx) => (
                                <li key={idx} className="text-sm text-purple-800">• {sug}</li>
                              ))}
                            </ul>
                          </Card>
                        )}

                        <div className="flex gap-3 mt-6">
                          <Button
                            onClick={handleGenerateFinalPrompt}
                            disabled={loading}
                            className="flex-1 bg-green-600 hover:bg-green-700"
                          >
                            <CheckCircle size={18} className="mr-2" />
                            Looks Good - Generate Prompt
                          </Button>
                          <Button
                            onClick={handleReset}
                            variant="outline"
                            className="flex-1"
                          >
                            <RefreshCw size={18} className="mr-2" />
                            Start Over
                          </Button>
                        </div>
                      </div>
                    )}
                  </>
                )}

                {step === 'final' && finalPrompt && (
                  <>
                    <div className="flex items-center justify-between mb-6">
                      <h2 className="text-2xl font-bold text-slate-900">Final Prompt Generated! 🎉</h2>
                      <Button onClick={handleReset} variant="outline" size="sm">
                        <RefreshCw size={16} className="mr-2" />
                        New Prompt
                      </Button>
                    </div>

                    <Card className="p-6 bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-300 mb-4">
                      <div className="flex items-start gap-3 mb-4">
                        <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
                        <div>
                          <h3 className="font-bold text-green-900 mb-1">Ready to Create Your Microsite</h3>
                          <p className="text-sm text-green-800">
                            Your prompt has been validated and optimized for {formData.industry} industry.
                            Copy it and paste into Lovable, Emergent, or Claude to generate your microsite.
                          </p>
                        </div>
                      </div>
                    </Card>

                    <div className="bg-slate-900 rounded-lg p-6 mb-4 max-h-96 overflow-y-auto">
                      <pre className="text-sm text-green-400 whitespace-pre-wrap font-mono">
                        {finalPrompt.prompt}
                      </pre>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <Button onClick={copyPrompt} className="bg-indigo-600 hover:bg-indigo-700">
                        <Copy size={16} className="mr-2" />
                        Copy Prompt
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => window.open('https://lovable.dev', '_blank')}
                      >
                        <ArrowRight size={16} className="mr-2" />
                        Open Lovable
                      </Button>
                    </div>
                  </>
                )}
              </Card>
            </div>

            {/* Right Panel - Chat/Validation */}
            <div>
              <Card className="p-6 bg-white shadow-xl border-2 border-slate-200 h-[600px] flex flex-col">
                <h3 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
                  <Sparkles className="text-indigo-600" />
                  AI Assistant
                </h3>

                <div className="flex-1 overflow-y-auto mb-4 space-y-3">
                  {chatMessages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center p-6">
                      <Lightbulb className="w-16 h-16 text-slate-300 mb-4" />
                      <p className="text-slate-600 text-sm">
                        Fill in the form and click "Validate" to start the AI-powered validation process.
                      </p>
                    </div>
                  ) : (
                    chatMessages.map((msg, idx) => (
                      <ChatMessage key={idx} message={msg.message} type={msg.type} />
                    ))
                  )}
                  <div ref={chatEndRef} />
                </div>

                {step === 'review' && (
                  <div className="border-t border-slate-200 pt-4">
                    <div className="flex gap-2">
                      <Input
                        value={userFeedback}
                        onChange={(e) => setUserFeedback(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleUserFeedbackSubmit()}
                        placeholder="Any changes or suggestions?"
                        disabled={loading}
                      />
                      <Button
                        onClick={handleUserFeedbackSubmit}
                        disabled={loading || !userFeedback.trim()}
                        size="icon"
                      >
                        <Send size={18} />
                      </Button>
                    </div>
                  </div>
                )}
              </Card>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

const StepIndicator = ({ active, completed, label }) => (
  <div className="flex flex-col items-center">
    <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold transition-all ${
      completed ? 'bg-green-600 text-white' : active ? 'bg-indigo-600 text-white' : 'bg-slate-200 text-slate-500'
    }`}>
      {completed ? <CheckCircle size={24} /> : active ? <Sparkles size={24} /> : <div className="w-3 h-3 rounded-full bg-slate-400" />}
    </div>
    <span className={`text-xs mt-2 font-medium ${active || completed ? 'text-slate-900' : 'text-slate-500'}`}>
      {label}
    </span>
  </div>
);

const ChatMessage = ({ message, type }) => {
  const bgColor = {
    system: 'bg-slate-100 text-slate-800',
    success: 'bg-green-100 text-green-800',
    error: 'bg-red-100 text-red-800',
    warning: 'bg-yellow-100 text-yellow-800',
    info: 'bg-blue-100 text-blue-800',
    user: 'bg-indigo-600 text-white ml-auto',
  }[type] || 'bg-slate-100 text-slate-800';

  return (
    <div className={`p-3 rounded-lg text-sm ${bgColor} ${type === 'user' ? 'max-w-[80%]' : ''}`}>
      {message}
    </div>
  );
};

export default GTMGenerator;
