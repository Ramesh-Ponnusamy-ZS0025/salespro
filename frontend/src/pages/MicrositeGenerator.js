import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { toast } from 'sonner';
import {
  Code2, Sparkles, ExternalLink, Loader2, CheckCircle, RefreshCw, Download, Trash2, MessageSquare, Send, FileText, X, Plus
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const INDUSTRIES = [
  'Fintech', 'Healthcare', 'E-commerce', 'SaaS', 'Manufacturing',
  'Real Estate', 'Education', 'Retail', 'Logistics', 'Financial Services',
  'Insurance', 'Technology', 'Telecommunications', 'Energy', 'Other'
];

const PERSONAS = [
  'CEO', 'CTO', 'CFO', 'COO', 'CMO',
  'VP of Sales', 'VP of Marketing', 'VP of Engineering', 'VP of Operations', 'VP of Product',
  'Sales Director', 'Marketing Director', 'IT Director', 'Operations Director', 'Product Director',
  'Sales Manager', 'Marketing Manager', 'Product Manager', 'Project Manager',
  'Business Owner', 'Founder', 'Entrepreneur',
  'Other'
];

const MicrositeGenerator = ({ user, onLogout }) => {
  const [configPanelOpen, setConfigPanelOpen] = useState(true);
  const [chatPanelOpen, setChatPanelOpen] = useState(false);
  const [previewPanelOpen, setPreviewPanelOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [deployedMicrosite, setDeployedMicrosite] = useState(null);
  const [availableDocuments, setAvailableDocuments] = useState([]);
  const [agents, setAgents] = useState([]);
  const [iframeKey, setIframeKey] = useState(0);
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [currentMicrositeId, setCurrentMicrositeId] = useState(null);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(null);
  const chatEndRef = useRef(null);

  const [formData, setFormData] = useState({
    company_name: '',
    industry: '',
    linkedin_url: '',
    agent_id: '',
    offering: '',
    pain_points: '',
    target_personas: [],
    use_cases: '',
    key_features: '',
    customer_profile_details: '',
    selected_documents: [],
    auto_pick_documents: false,
  });

  useEffect(() => {
    // Fetch available documents and agents on component mount
    const fetchDocuments = async () => {
      try {
        const response = await axios.get(`${API}/document-files/for-campaign`);
        const docs = response.data.documents || [];
        console.log('Fetched documents:', docs);
        setAvailableDocuments(docs);
        if (docs.length > 0) {
          toast.success(`Loaded ${docs.length} case studies`);
        }
      } catch (error) {
        console.error('Failed to fetch documents:', error);
        toast.error('Failed to load case studies');
      }
    };

    const fetchAgents = async () => {
      try {
        const response = await axios.get(`${API}/agents`);
        setAgents(response.data || []);
      } catch (error) {
        console.error('Failed to fetch agents:', error);
        toast.error('Failed to load agents');
      }
    };

    fetchDocuments();
    fetchAgents();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const togglePersona = (persona) => {
    setFormData(prev => {
      const currentPersonas = prev.target_personas || [];
      if (currentPersonas.includes(persona)) {
        return {
          ...prev,
          target_personas: currentPersonas.filter(p => p !== persona)
        };
      } else {
        return {
          ...prev,
          target_personas: [...currentPersonas, persona]
        };
      }
    });
  };

  const handleAgentSelect = (agentId) => {
    const selectedAgent = agents.find(agent => agent.id === agentId);
    if (selectedAgent) {
      setFormData(prev => ({
        ...prev,
        agent_id: agentId,
        offering: selectedAgent.value_props?.join(', ') || prev.offering,
        pain_points: selectedAgent.pain_points?.join(', ') || prev.pain_points,
        target_personas: selectedAgent.personas || prev.target_personas,
      }));
      toast.success(`Agent "${selectedAgent.agent_name}" configuration loaded!`);
    } else {
      setFormData(prev => ({ ...prev, agent_id: agentId }));
    }
  };

  const addMessage = (content, sender = 'assistant') => {
    setMessages(prev => [...prev, { content, sender, timestamp: new Date() }]);
  };

  const handleStartChat = () => {
    if (!formData.company_name || !formData.industry || !formData.agent_id) {
      toast.error('Please fill in required fields (Company Name, Industry, Agent)');
      return;
    }

    setChatPanelOpen(true);
    addMessage(`Great! I'm ready to help you generate a microsite for **${formData.company_name}**. I've loaded the configuration from the selected agent.\n\nWould you like me to:\n1. **Generate the site** with current configuration\n2. **Make adjustments** to any section\n3. **Add more details** before generating\n\nType your choice or provide additional instructions.`, 'assistant');
  };

  const handleUserMessage = async () => {
    if (!userInput.trim() || loading || isRegenerating) return;

    const userMsg = userInput.trim();
    addMessage(userMsg, 'user');
    setUserInput('');
    setLoading(true);

    try {
      const lowerMsg = userMsg.toLowerCase();

      // Check if user is requesting changes to existing microsite
      if (currentMicrositeId && deployedMicrosite && (
        lowerMsg.includes('change') || lowerMsg.includes('modify') ||
        lowerMsg.includes('update') || lowerMsg.includes('make it') ||
        lowerMsg.includes('can you') || lowerMsg.includes('please') ||
        lowerMsg.includes('different') || lowerMsg.includes('more') ||
        lowerMsg.includes('less') || lowerMsg.includes('add') ||
        lowerMsg.includes('remove') || lowerMsg.includes('replace')
      )) {
        addMessage('I understand you want changes! Let me regenerate the microsite with your feedback... 🔄', 'assistant');
        await handleRegenerateMicrosite(userMsg);
      } else if (lowerMsg.includes('1') || lowerMsg.includes('generate')) {
        addMessage('Perfect! Generating your microsite now... 🚀', 'assistant');
        await handleGenerateMicrosite();
      } else if (lowerMsg.includes('2') || lowerMsg.includes('adjust')) {
        addMessage('What would you like to adjust? You can modify:\n- Target personas\n- Use cases\n- Key features\n- Customer profile details\n- Case studies selection\n\nPlease let me know what changes you\'d like to make.', 'assistant');
      } else if (lowerMsg.includes('3') || lowerMsg.includes('detail')) {
        addMessage('Great! What additional details would you like to add? You can provide information about:\n- Specific use cases for your prospects\n- Key features to highlight\n- Target customer profile details\n- Any other relevant context', 'assistant');
      } else if (currentMicrositeId && deployedMicrosite) {
        // If microsite already generated, treat as feedback
        addMessage('I understand. Let me incorporate your feedback and regenerate the microsite... 🔄', 'assistant');
        await handleRegenerateMicrosite(userMsg);
      } else {
        addMessage('Got it! Feel free to provide more details, or type "generate" when you\'re ready to create the microsite.', 'assistant');
      }
    } catch (error) {
      addMessage('I apologize, I had trouble processing that. Could you rephrase?', 'assistant');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateMicrosite = async () => {
    // Validation
    if (!formData.company_name || !formData.industry || !formData.agent_id) {
      toast.error('Please fill in required fields (Company Name, Industry, Agent)');
      return;
    }

    setLoading(true);
    setPreviewPanelOpen(true); // Open preview panel immediately
    setGenerationProgress({
      status: 'preparing',
      message: 'Initializing microsite generation...',
      progress: 0
    });

    try {
      // Simulate progress updates
      const progressSteps = [
        { progress: 10, message: 'Analyzing company context and industry...' },
        { progress: 20, message: 'Auto-picking relevant case studies...' },
        { progress: 30, message: 'Detecting optimal theme and design language...' },
        { progress: 40, message: 'Planning layout architecture...' },
        { progress: 50, message: 'Generating strategic content...' },
        { progress: 60, message: 'Creating adaptive UI components...' },
        { progress: 75, message: 'Implementing premium sales design...' },
        { progress: 85, message: 'Evaluating design quality...' },
        { progress: 95, message: 'Finalizing microsite...' }
      ];

      let currentStep = 0;
      const progressInterval = setInterval(() => {
        if (currentStep < progressSteps.length) {
          setGenerationProgress({
            status: 'generating',
            ...progressSteps[currentStep]
          });
          currentStep++;
        }
      }, 8000); // Update every 8 seconds

      // Prepare data for backend
      const requestData = {
        company_name: formData.company_name,
        industry: formData.industry,
        linkedin_url: formData.linkedin_url,
        offering: formData.offering,
        pain_points: formData.pain_points.split(',').map(p => p.trim()).filter(Boolean),
        target_personas: Array.isArray(formData.target_personas) ? formData.target_personas : formData.target_personas.split(',').map(p => p.trim()).filter(Boolean),
        use_cases: formData.use_cases.split(',').map(p => p.trim()).filter(Boolean),
        key_features: formData.key_features.split(',').map(p => p.trim()).filter(Boolean),
        customer_profile_details: formData.customer_profile_details,
        selected_documents: formData.auto_pick_documents ? [] : formData.selected_documents,
        auto_pick_documents: formData.auto_pick_documents,
      };

      const response = await axios.post(`${API}/microsite/generate`, requestData);

      clearInterval(progressInterval);
      setGenerationProgress({
        status: 'complete',
        message: 'Microsite generated successfully!',
        progress: 100
      });

      setTimeout(() => {
        setDeployedMicrosite(response.data);
        setCurrentMicrositeId(response.data.microsite_id);
        setIframeKey(prev => prev + 1); // Force iframe reload
        setGenerationProgress(null);
        addMessage('✅ **Microsite Generated Successfully!**\n\nYour microsite is now available in the preview panel. You can review it and let me know if you\'d like any changes!\n\n💡 **Try saying:**\n- "Make it more modern"\n- "Change the colors to blue and green"\n- "Add more content about our key features"\n- "Make the headline more bold"', 'assistant');
        toast.success('Microsite generated successfully!');
      }, 1000);
    } catch (error) {
      console.error('Generation error:', error);
      setGenerationProgress({
        status: 'error',
        message: 'Failed to generate microsite',
        progress: 0
      });
      setTimeout(() => {
        setGenerationProgress(null);
        setPreviewPanelOpen(false);
      }, 2000);
      addMessage('❌ Failed to generate microsite. Please try again.', 'assistant');
      toast.error(error.response?.data?.detail || 'Failed to generate microsite');
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerateMicrosite = async (feedback) => {
    if (!currentMicrositeId) {
      addMessage('❌ No microsite to regenerate yet. Please generate one first!', 'assistant');
      return;
    }

    setIsRegenerating(true);
    setGenerationProgress({
      status: 'regenerating',
      message: 'Processing your feedback...',
      progress: 10
    });

    try {
      // Simulate progress for regeneration
      const progressSteps = [
        { progress: 20, message: 'Analyzing your feedback...' },
        { progress: 40, message: 'Updating design strategy...' },
        { progress: 60, message: 'Regenerating content...' },
        { progress: 80, message: 'Applying design improvements...' },
        { progress: 95, message: 'Finalizing changes...' }
      ];

      let currentStep = 0;
      const progressInterval = setInterval(() => {
        if (currentStep < progressSteps.length) {
          setGenerationProgress({
            status: 'regenerating',
            ...progressSteps[currentStep]
          });
          currentStep++;
        }
      }, 6000); // Update every 6 seconds

      const requestData = {
        microsite_id: currentMicrositeId,
        feedback: feedback,
        company_name: formData.company_name,
        industry: formData.industry,
        offering: formData.offering,
        pain_points: formData.pain_points.split(',').map(p => p.trim()).filter(Boolean),
        target_personas: Array.isArray(formData.target_personas) ? formData.target_personas : formData.target_personas.split(',').map(p => p.trim()).filter(Boolean),
        use_cases: formData.use_cases.split(',').map(p => p.trim()).filter(Boolean),
        key_features: formData.key_features.split(',').map(p => p.trim()).filter(Boolean),
      };

      const response = await axios.post(`${API}/microsite/regenerate`, requestData);

      clearInterval(progressInterval);
      setGenerationProgress({
        status: 'complete',
        message: 'Microsite updated successfully!',
        progress: 100
      });

      setTimeout(() => {
        setDeployedMicrosite(response.data);
        setIframeKey(prev => prev + 1); // Force iframe reload
        setGenerationProgress(null);
        addMessage(`✅ **Microsite Updated!**\n\nI've regenerated the microsite with your feedback. The preview has been refreshed with the changes!\n\n💡 Want more changes? Just let me know!`, 'assistant');
        toast.success('Microsite regenerated with your changes!');
      }, 1000);
    } catch (error) {
      console.error('Regeneration error:', error);
      setGenerationProgress({
        status: 'error',
        message: 'Failed to regenerate microsite',
        progress: 0
      });
      setTimeout(() => setGenerationProgress(null), 2000);
      addMessage('❌ Failed to regenerate microsite. Please try again or be more specific with your feedback.', 'assistant');
      toast.error(error.response?.data?.detail || 'Failed to regenerate microsite');
    } finally {
      setIsRegenerating(false);
    }
  };

  const handleStopMicrosite = async () => {
    if (!deployedMicrosite) return;

    try {
      await axios.delete(`${API}/microsite/${deployedMicrosite.microsite_id}`);
      setDeployedMicrosite(null);
      toast.success('Microsite stopped successfully');
    } catch (error) {
      toast.error('Failed to stop microsite');
    }
  };

  const handleClear = () => {
    setDeployedMicrosite(null);
    setCurrentMicrositeId(null);
    setMessages([]);
    setChatPanelOpen(false);
    setPreviewPanelOpen(false);
    setIsRegenerating(false);
    setFormData({
      company_name: '',
      industry: '',
      linkedin_url: '',
      agent_id: '',
      offering: '',
      pain_points: '',
      target_personas: [],
      use_cases: '',
      key_features: '',
      customer_profile_details: '',
      selected_documents: [],
      auto_pick_documents: false,
    });
  };

  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="flex h-full bg-white">
        {/* Config Panel */}
        <div className={`flex-shrink-0 transition-all duration-300 border-r border-slate-200 bg-gray-50 ${
          configPanelOpen ? 'w-80' : 'w-0'
        } overflow-hidden`}>
          <div className="h-full flex flex-col">
            <div className="p-4 border-b border-slate-200 bg-white">
              <div className="flex items-center gap-2">
                <Code2 className="w-6 h-6 text-indigo-600" />
                <h2 className="text-lg font-bold text-slate-900">Configuration</h2>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              <div>
                <Label className="text-sm font-medium">Company Name *</Label>
                <Input
                  value={formData.company_name}
                  onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                  placeholder="TECU Credit Union"
                  className="mt-1"
                />
              </div>

              <div>
                <Label className="text-sm font-medium">Industry *</Label>
                <select
                  value={formData.industry}
                  onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                  className="mt-1 w-full border border-slate-300 rounded-md px-3 py-2 text-sm"
                >
                  <option value="">Select Industry</option>
                  {INDUSTRIES.map(ind => <option key={ind} value={ind}>{ind}</option>)}
                </select>
              </div>

              <div>
                <Label className="text-sm font-medium">LinkedIn URL</Label>
                <Input
                  value={formData.linkedin_url}
                  onChange={(e) => setFormData({ ...formData, linkedin_url: e.target.value })}
                  placeholder="https://linkedin.com/company/tecu"
                  className="mt-1"
                />
              </div>

              <div>
                <Label className="text-sm font-medium">Select Agent *</Label>
                <Select value={formData.agent_id} onValueChange={handleAgentSelect}>
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="Choose agent" />
                  </SelectTrigger>
                  <SelectContent>
                    {agents.map(agent => (
                      <SelectItem key={agent.id} value={agent.id}>
                        {agent.agent_name}
                        {agent.submitted_by_leaders && ' ⭐'}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-slate-500 mt-1">
                  {agents.length} agent(s) available. Selecting an agent will populate pain points and offerings.
                </p>
              </div>

              <div>
                <Label className="text-sm font-medium">Target Decision Makers *</Label>
                <Select onValueChange={togglePersona}>
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder={
                      formData.target_personas.length > 0
                        ? `${formData.target_personas.length} persona${formData.target_personas.length > 1 ? 's' : ''} selected`
                        : "Select target personas"
                    } />
                  </SelectTrigger>
                  <SelectContent>
                    {PERSONAS.map((persona) => (
                      <SelectItem key={persona} value={persona}>
                        {persona}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {formData.target_personas.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {formData.target_personas.map((persona) => (
                      <span
                        key={persona}
                        className="inline-flex items-center gap-1 px-2 py-1 bg-indigo-100 text-indigo-800 rounded-full text-xs"
                      >
                        {persona}
                        <button
                          onClick={() => togglePersona(persona)}
                          className="hover:bg-indigo-200 rounded-full p-0.5"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <Label className="text-sm font-medium">Use Cases (comma-separated)</Label>
                <Textarea
                  value={formData.use_cases}
                  onChange={(e) => setFormData({ ...formData, use_cases: e.target.value })}
                  placeholder="Digital account opening, Instant card issuance, AI chatbot"
                  rows={2}
                  className="mt-1"
                />
              </div>

              <div>
                <Label className="text-sm font-medium">Key Features (comma-separated)</Label>
                <Textarea
                  value={formData.key_features}
                  onChange={(e) => setFormData({ ...formData, key_features: e.target.value })}
                  placeholder="Real-time status tracking, Document automation, Analytics dashboard"
                  rows={2}
                  className="mt-1"
                />
              </div>

              <div>
                <Label className="text-sm font-medium">Customer Profile Details</Label>
                <Textarea
                  value={formData.customer_profile_details}
                  onChange={(e) => setFormData({ ...formData, customer_profile_details: e.target.value })}
                  placeholder="Additional context about target customers..."
                  rows={2}
                  className="mt-1"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label className="text-sm font-medium">Case Studies & Documents</Label>
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="auto-pick"
                      checked={formData.auto_pick_documents}
                      onChange={(e) => {
                        setFormData(prev => ({
                          ...prev,
                          auto_pick_documents: e.target.checked,
                          selected_documents: e.target.checked ? [] : prev.selected_documents
                        }));
                      }}
                      className="rounded"
                    />
                    <label htmlFor="auto-pick" className="cursor-pointer text-sm">
                      Auto Pick
                    </label>
                  </div>
                </div>

                {!formData.auto_pick_documents && (
                  <div className="border rounded-lg p-3 max-h-48 overflow-y-auto space-y-2 bg-white">
                    {availableDocuments.length === 0 ? (
                      <p className="text-sm text-slate-500">No documents available</p>
                    ) : (
                      availableDocuments.map(doc => (
                        <div
                          key={doc.id}
                          className="flex items-start gap-2 p-2 hover:bg-slate-50 rounded cursor-pointer"
                          onClick={() => {
                            setFormData(prev => ({
                              ...prev,
                              selected_documents: prev.selected_documents.includes(doc.id)
                                ? prev.selected_documents.filter(id => id !== doc.id)
                                : [...prev.selected_documents, doc.id]
                            }));
                          }}
                        >
                          <input
                            type="checkbox"
                            checked={formData.selected_documents.includes(doc.id)}
                            readOnly
                            className="mt-1 rounded"
                          />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-slate-900 truncate">
                              {doc.title || doc.filename}
                            </p>
                            {doc.category && (
                              <p className="text-xs text-slate-500">{doc.category}</p>
                            )}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                )}

                {formData.auto_pick_documents && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800">
                    ✨ Case studies will be automatically selected based on industry and pain points
                  </div>
                )}
              </div>

              <Button
                onClick={handleStartChat}
                disabled={loading || chatPanelOpen}
                className="w-full bg-indigo-600 hover:bg-indigo-700"
              >
                <MessageSquare className="w-4 h-4 mr-2" />
                {chatPanelOpen ? 'Chat Active' : 'Start Configuration Chat'}
              </Button>

              {(deployedMicrosite || chatPanelOpen) && (
                <Button
                  onClick={handleClear}
                  variant="outline"
                  className="w-full"
                >
                  Clear & Start New
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Chat Panel */}
        <div className={`flex-shrink-0 transition-all duration-300 border-r border-slate-200 bg-white ${
          chatPanelOpen ? 'flex-1' : 'w-0'
        } overflow-hidden flex flex-col`}>
          <div className="border-b border-slate-200 p-4 bg-white">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-6 h-6 text-indigo-600" />
              <h1 className="text-xl font-bold text-slate-900">AI Assistant</h1>
            </div>
            <p className="text-sm text-slate-600 mt-1">Refine your configuration and generate your microsite.</p>
          </div>

          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <MessageSquare className="w-16 h-16 text-slate-300 mb-4" />
                <h3 className="text-lg font-semibold text-slate-900">Welcome to Microsite Generator</h3>
                <p className="text-slate-600 mt-2 max-w-md">
                  Configure your details on the left, then click "Start Configuration Chat" to begin.
                </p>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <ChatBubble key={idx} message={msg} />
              ))
            )}
            <div ref={chatEndRef} />
          </div>

          <div className="border-t border-slate-200 p-4 bg-white">
            <div className="flex gap-2">
              <Input
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleUserMessage()}
                placeholder={
                  isRegenerating ? "Regenerating with your changes..." :
                  deployedMicrosite ? "Request changes to the microsite..." :
                  "Type your message or 'generate' to create microsite..."
                }
                disabled={loading || isRegenerating || messages.length === 0}
                className="flex-1"
              />
              <Button
                onClick={handleUserMessage}
                disabled={loading || isRegenerating || !userInput.trim()}
                className="bg-indigo-600 hover:bg-indigo-700"
              >
                {loading || isRegenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </Button>
            </div>
          </div>
        </div>

        {/* Microsite Preview Panel */}
        {previewPanelOpen && (
          <div className="flex-shrink-0 w-[50%] border-l border-slate-200 bg-white flex flex-col">
            <div className="border-b border-slate-200 p-4 bg-white">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Code2 className="w-6 h-6 text-indigo-600" />
                  <h1 className="text-xl font-bold text-slate-900">
                    {generationProgress ? 'Generating Microsite' : 'Microsite Preview'}
                  </h1>
                </div>
                <div className="flex items-center gap-2">
                  {deployedMicrosite && !generationProgress && (
                    <>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => window.open(deployedMicrosite.microsite_url, '_blank')}
                      >
                        <ExternalLink className="w-4 h-4 mr-2" />
                        Open in New Tab
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setIframeKey(prev => prev + 1)}
                      >
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Refresh
                      </Button>
                    </>
                  )}
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => {
                      setPreviewPanelOpen(false);
                      setGenerationProgress(null);
                    }}
                  >
                    <X size={18} />
                  </Button>
                </div>
              </div>
            </div>

            <div className="flex-1 overflow-hidden bg-slate-50">
              <div className="h-full flex flex-col">
                {generationProgress ? (
                  /* Progress Display */
                  <div className="flex-1 flex items-center justify-center p-8">
                    <div className="max-w-md w-full space-y-6">
                      <div className="text-center">
                        <Sparkles className={`w-16 h-16 mx-auto mb-4 ${
                          generationProgress.status === 'error' ? 'text-red-500' :
                          generationProgress.status === 'complete' ? 'text-green-500' :
                          'text-indigo-500 animate-pulse'
                        }`} />
                        <h3 className="text-xl font-bold text-slate-900 mb-2">
                          {generationProgress.status === 'error' ? 'Generation Failed' :
                           generationProgress.status === 'complete' ? 'Success!' :
                           generationProgress.status === 'regenerating' ? 'Regenerating Microsite' :
                           'Generating Your Microsite'}
                        </h3>
                        <p className="text-slate-600 mb-6">
                          {generationProgress.message}
                        </p>
                      </div>

                      {/* Progress Bar */}
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm text-slate-600">
                          <span>Progress</span>
                          <span className="font-semibold">{generationProgress.progress}%</span>
                        </div>
                        <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all duration-500 ${
                              generationProgress.status === 'error' ? 'bg-red-500' :
                              generationProgress.status === 'complete' ? 'bg-green-500' :
                              'bg-gradient-to-r from-indigo-500 to-purple-500'
                            }`}
                            style={{ width: `${generationProgress.progress}%` }}
                          />
                        </div>
                      </div>

                      {/* Generation Steps */}
                      {generationProgress.status !== 'error' && generationProgress.status !== 'complete' && (
                        <div className="bg-white rounded-lg p-4 border border-slate-200">
                          <h4 className="text-sm font-semibold text-slate-900 mb-3">Generation Steps:</h4>
                          <div className="space-y-2 text-sm text-slate-600">
                            <div className="flex items-center gap-2">
                              <CheckCircle className="w-4 h-4 text-green-500" />
                              <span>Context Analysis</span>
                            </div>
                            <div className="flex items-center gap-2">
                              {generationProgress.progress >= 20 ? (
                                <CheckCircle className="w-4 h-4 text-green-500" />
                              ) : (
                                <Loader2 className="w-4 h-4 animate-spin text-indigo-500" />
                              )}
                              <span>Case Study Selection</span>
                            </div>
                            <div className="flex items-center gap-2">
                              {generationProgress.progress >= 40 ? (
                                <CheckCircle className="w-4 h-4 text-green-500" />
                              ) : (
                                <div className="w-4 h-4 rounded-full border-2 border-slate-300" />
                              )}
                              <span>Layout Architecture</span>
                            </div>
                            <div className="flex items-center gap-2">
                              {generationProgress.progress >= 60 ? (
                                <CheckCircle className="w-4 h-4 text-green-500" />
                              ) : (
                                <div className="w-4 h-4 rounded-full border-2 border-slate-300" />
                              )}
                              <span>Content Generation</span>
                            </div>
                            <div className="flex items-center gap-2">
                              {generationProgress.progress >= 75 ? (
                                <CheckCircle className="w-4 h-4 text-green-500" />
                              ) : (
                                <div className="w-4 h-4 rounded-full border-2 border-slate-300" />
                              )}
                              <span>UI Implementation</span>
                            </div>
                            <div className="flex items-center gap-2">
                              {generationProgress.progress >= 95 ? (
                                <CheckCircle className="w-4 h-4 text-green-500" />
                              ) : (
                                <div className="w-4 h-4 rounded-full border-2 border-slate-300" />
                              )}
                              <span>Quality Evaluation</span>
                            </div>
                          </div>
                        </div>
                      )}

                      {generationProgress.status === 'error' && (
                        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
                          <p className="text-sm text-red-700">Please try again or contact support if the issue persists.</p>
                        </div>
                      )}
                    </div>
                  </div>
                ) : deployedMicrosite ? (
                  /* Deployed Microsite Preview */
                  <>
                    {/* Success banner */}
                    <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-b-2 border-green-300 p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <CheckCircle className="w-5 h-5 text-green-600" />
                        <span className="font-bold text-green-900 text-lg">
                          {deployedMicrosite.project_name}
                        </span>
                        <span className="ml-auto text-xs text-green-700">
                          Generated in {(deployedMicrosite.generation_time_ms / 1000).toFixed(1)}s
                        </span>
                      </div>
                      <p className="text-sm text-green-700">
                        {deployedMicrosite.description}
                      </p>
                      <div className="flex items-center gap-2 mt-2">
                        <code className="text-xs font-mono bg-white px-2 py-1 rounded border border-green-200 text-indigo-600">
                          {deployedMicrosite.microsite_url}
                        </code>
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-xs"
                          onClick={() => {
                            navigator.clipboard.writeText(deployedMicrosite.microsite_url);
                            toast.success('URL copied to clipboard');
                          }}
                        >
                          Copy URL
                        </Button>
                      </div>
                    </div>

                    {/* Iframe viewer */}
                    <div className="flex-1 relative">
                      <iframe
                        key={iframeKey}
                        src={deployedMicrosite.microsite_url}
                        className="absolute inset-0 w-full h-full border-0"
                        title="Microsite Preview"
                        sandbox="allow-scripts allow-same-origin allow-forms"
                      />
                    </div>
                  </>
                ) : (
                  /* Empty state */
                  <div className="flex-1 flex items-center justify-center p-8">
                    <div className="text-center text-slate-500">
                      <Code2 className="w-16 h-16 mx-auto mb-4 text-slate-300" />
                      <p>Waiting for microsite generation...</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

const ChatBubble = ({ message }) => {
  const isUser = message.sender === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[75%] ${isUser ? '' : 'space-y-3'}`}>
        <div className={`rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-indigo-600 text-white'
            : 'bg-slate-100 border border-slate-200 text-slate-900'
        }`}>
          <div className="text-sm whitespace-pre-wrap leading-relaxed">
            {message.content.split('**').map((part, idx) =>
              idx % 2 === 1 ? <strong key={idx}>{part}</strong> : part
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MicrositeGenerator;
