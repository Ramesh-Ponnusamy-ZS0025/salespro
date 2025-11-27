import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { toast } from 'sonner';
import { 
  Sparkles, Send, Copy, Download, X, MessageSquare, FileText, CheckCircle, Loader2
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const INDUSTRIES = [
  'Fintech', 'Healthcare', 'E-commerce', 'SaaS', 'Manufacturing',
  'Real Estate', 'Education', 'Retail', 'Logistics', 'Other'
];

const GTMGenerator = ({ user, onLogout }) => {
  const [configPanelOpen, setConfigPanelOpen] = useState(true);
  const [promptPanelOpen, setPromptPanelOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [finalPrompt, setFinalPrompt] = useState(null);
  const [validationResult, setValidationResult] = useState(null);
  const [userAdjustments, setUserAdjustments] = useState(''); // Collect all user adjustments
  const [availableDocuments, setAvailableDocuments] = useState([]);
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
    customer_profile_details: '', // NEW FIELD
    selected_documents: [], // NEW FIELD
    auto_pick_documents: false, // NEW FIELD
  });

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    // Fetch available documents on component mount
    const fetchDocuments = async () => {
      try {
        const response = await axios.get(`${API}/document-files/for-campaign`);
        setAvailableDocuments(response.data.documents || []);
      } catch (error) {
        console.error('Failed to fetch documents:', error);
      }
    };
    fetchDocuments();
  }, []);

  const addMessage = (content, sender = 'assistant') => {
    setMessages(prev => [...prev, { content, sender, timestamp: new Date() }]);
  };

  const handleStartGeneration = async () => {
    if (!formData.company_name || !formData.industry || !formData.offering || !formData.pain_points) {
      toast.error('Please fill in required fields (marked with *)');
      return;
    }

    setLoading(true);
    setUserAdjustments(''); // Reset adjustments for fresh conversation
    addMessage(`Great! Let me analyze the information for **${formData.company_name}**...`, 'assistant');

    try {
      const response = await axios.post(`${API}/gtm/validate`, {
        ...formData,
        pain_points: formData.pain_points.split(',').map(p => p.trim()).filter(Boolean),
        target_personas: formData.target_personas.split(',').map(p => p.trim()).filter(Boolean),
        use_cases: formData.use_cases.split(',').map(p => p.trim()).filter(Boolean),
        key_features: formData.key_features.split(',').map(p => p.trim()).filter(Boolean),
      });

      setValidationResult(response.data);

      let validationMsg = `✅ **Validation Complete**\n\n`;
      validationMsg += `📊 **Company**: ${formData.company_name}\n`;
      validationMsg += `🏢 **Industry**: ${formData.industry}\n\n`;

      if (response.data.has_use_cases) {
        validationMsg += `✨ Found **${response.data.use_case_count} industry-specific use cases** for ${formData.industry}!\n\n`;
      } else {
        validationMsg += `ℹ️ No specific use cases found for ${formData.industry}. I'll use general best practices.\n\n`;
      }

      if (response.data.suggestions?.length > 0) {
        validationMsg += `💡 **Suggestions to improve your microsite:**\n`;
        response.data.suggestions.forEach((sug, idx) => {
          validationMsg += `${idx + 1}. ${sug}\n`;
        });
        validationMsg += `\n`;
      }

      validationMsg += `Would you like me to:\n`;
      validationMsg += `1. **Generate the prompt** as-is\n`;
      validationMsg += `2. **Make adjustments** based on suggestions\n`;
      validationMsg += `3. **Add more details** to any section\n\n`;
      validationMsg += `Type your choice or provide additional instructions.`;

      addMessage(validationMsg, 'assistant');

    } catch (error) {
      addMessage('❌ Validation failed. Please check your inputs and try again.', 'assistant');
      toast.error(error.response?.data?.detail || 'Validation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickAction = (action) => {
    setUserInput(action);
    setTimeout(() => {
      handleUserMessage();
    }, 100);
  };

 const handleUserMessage = async () => {
    if (!userInput.trim() || loading) return;

    const userMsg = userInput.trim();
    addMessage(userMsg, 'user');

    // Smart detection: Only SHORT, EXACT generate commands should trigger generation
    const msgLower = userMsg.toLowerCase().trim();
    const exactGenerateCommands = ['generate', 'yes', 'go ahead', 'proceed', '1', '2', '3',
                                   'generate prompt', 'lets go', "let's go", 'ready',
                                   'generate it', 'create it', 'ok', 'sure'];

    // Only trigger generate if:
    // 1. It's an exact match with a command, OR
    // 2. The message is very short (< 5 words) and contains a generate keyword
    const words = userMsg.split(/\s+/);
    const isGenerateCommand = exactGenerateCommands.includes(msgLower) ||
                             (words.length <= 5 && exactGenerateCommands.some(cmd => msgLower.includes(cmd)));

    // Create a variable to store current adjustments
    let currentAdjustments = userAdjustments;

    // ALWAYS collect user messages as adjustments (unless it's a clear generate command)
    if (!isGenerateCommand) {
      // This is an adjustment, collect it
      currentAdjustments = userAdjustments ? `${userAdjustments}\n\n${userMsg}` : userMsg;
      setUserAdjustments(currentAdjustments);
      console.log('📝 Added to user adjustments:', userMsg);
      console.log('📋 Total adjustments so far:', currentAdjustments);
    } else {
      console.log('🚀 Detected generate command:', userMsg);
    }

    setUserInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${API}/gtm/process-feedback`, {
        feedback: userMsg,
        validation_result: validationResult,
        form_data: formData,
      });

      // Update form data if backend extracted new information
      if (response.data.updated_form_data) {
        setFormData(prev => ({ ...prev, ...response.data.updated_form_data }));
      }

      if (response.data.should_regenerate || response.data.action === 'generate') {
        addMessage(response.data.message, 'assistant');
        await new Promise(resolve => setTimeout(resolve, 500));
        addMessage('Generating your comprehensive microsite prompt... 🚀', 'assistant');

        try {
          // FIXED: Use currentAdjustments instead of state (which may not be updated yet)
          const finalFormData = {
            ...formData,
            user_adjustments: currentAdjustments // Use the latest adjustments
          };

          console.log('📤 Sending to backend with ALL user adjustments:');
          console.log('User adjustments length:', currentAdjustments?.length || 0);
          console.log('User adjustments content:', currentAdjustments);
          console.log('Full payload:', {
            form_data: finalFormData,
            validation_result: validationResult,
          });

          const promptResponse = await axios.post(`${API}/gtm/generate-final-prompt`, {
            form_data: finalFormData,
            validation_result: validationResult,
          });

          setFinalPrompt(promptResponse.data);
          setPromptPanelOpen(true);

          addMessage(
            '✅ **Prompt Generated Successfully!**\n\nYour production-ready microsite prompt is now available in the preview panel on the right.',
            'assistant'
          );
        } catch (error) {
          console.error('Generation error:', error.response?.data);
          addMessage('❌ Failed to generate prompt. Please try again.', 'assistant');
          toast.error(error.response?.data?.detail || 'Generation failed');
        }
      } else {
        addMessage(response.data.message, 'assistant');
        if (response.data.updated_validation) {
          setValidationResult(response.data.updated_validation);
        }
      }

    } catch (error) {
      console.error('Feedback processing error:', error.response?.data);
      addMessage('I had trouble processing that. Could you provide more details or try rephrasing?', 'assistant');
      toast.error('Processing failed');
    } finally {
      setLoading(false);
    }
  };

  const copyPrompt = () => {
    if (finalPrompt?.prompt) {
      navigator.clipboard.writeText(finalPrompt.prompt);
      toast.success('Prompt copied to clipboard!');
    }
  };

  const handleReset = () => {
    setMessages([]);
    setFinalPrompt(null);
    setValidationResult(null);
    setUserAdjustments('');
    setPromptPanelOpen(false);
    setFormData({
      company_name: '',
      industry: '',
      linkedin_url: '',
      offering: '',
      pain_points: '',
      target_personas: '',
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
              <h2 className="text-lg font-bold text-slate-900">Configuration</h2>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              <div>
                <Label className="text-sm font-medium">Company Name *</Label>
                <Input
                  value={formData.company_name}
                  onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                  placeholder="Acme Corporation"
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
                  placeholder="https://linkedin.com/company/acme"
                  className="mt-1"
                />
              </div>

              <div>
                <Label className="text-sm font-medium">Your Offering *</Label>
                <Textarea
                  value={formData.offering}
                  onChange={(e) => setFormData({ ...formData, offering: e.target.value })}
                  placeholder="AI-powered platform that..."
                  rows={3}
                  className="mt-1"
                />
              </div>

              <div>
                <Label className="text-sm font-medium">Pain Points (comma-separated) *</Label>
                <Textarea
                  value={formData.pain_points}
                  onChange={(e) => setFormData({ ...formData, pain_points: e.target.value })}
                  placeholder="Manual processes, Low efficiency"
                  rows={2}
                  className="mt-1"
                />
              </div>

              <div>
                <Label className="text-sm font-medium">Target Decision Makers *</Label>
                <Textarea
                  value={formData.target_personas}
                  onChange={(e) => setFormData({ ...formData, target_personas: e.target.value })}
                  placeholder="CEO, CTO, Sales Director"
                  rows={2}
                  className="mt-1"
                />
              </div>

              <div>
                <Label className="text-sm font-medium">Use Cases (optional)</Label>
                <Textarea
                  value={formData.use_cases}
                  onChange={(e) => setFormData({ ...formData, use_cases: e.target.value })}
                  placeholder="Automation, Analytics"
                  rows={2}
                  className="mt-1"
                />
              </div>

              <div>
                <Label className="text-sm font-medium">Key Features (optional)</Label>
                <Textarea
                  value={formData.key_features}
                  onChange={(e) => setFormData({ ...formData, key_features: e.target.value })}
                  placeholder="AI-powered, Cloud-based"
                  rows={2}
                  className="mt-1"
                />
              </div>

              <div>
                <Label className="text-sm font-medium">Customer Profile Details (optional)</Label>
                <Textarea
                  value={formData.customer_profile_details}
                  onChange={(e) => setFormData({ ...formData, customer_profile_details: e.target.value })}
                  placeholder="Add specific details about customer profiles, buying behavior, decision-making process, etc."
                  rows={3}
                  className="mt-1"
                />
              </div>

              {/* Case Studies Picker */}
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
                            onChange={() => {}} // Handled by parent onClick
                            className="mt-1"
                          />
                          <div className="flex-1">
                            <div className="font-medium text-sm">{doc.title}</div>
                            <div className="text-xs text-slate-500">
                              {doc.category} • {doc.doc_type}
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                )}

                {formData.auto_pick_documents && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800">
                    ✨ Documents will be automatically selected based on campaign relevance
                  </div>
                )}
              </div>

              <Button
                onClick={handleStartGeneration}
                disabled={loading}
                className="w-full bg-indigo-600 hover:bg-indigo-700"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Generate Prompt
              </Button>

              <Button
                onClick={handleReset}
                variant="outline"
                className="w-full"
              >
                <X className="w-4 h-4 mr-2" />
                Reset
              </Button>
            </div>
          </div>
        </div>

        {/* Chat Panel */}
        <div className="flex-1 flex flex-col bg-white">
          <div className="border-b border-slate-200 p-4 bg-white">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-6 h-6 text-indigo-600" />
              <h1 className="text-xl font-bold text-slate-900">AI Assistant</h1>
            </div>
            <p className="text-sm text-slate-600 mt-1">Configure your prospect details on the left, then click "Generate Prompt" to start a conversation with AI.</p>
          </div>

          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <MessageSquare className="w-16 h-16 text-slate-300 mb-4" />
                <h3 className="text-lg font-semibold text-slate-900">Welcome to GTM Generator</h3>
                <p className="text-slate-600 mt-2 max-w-md">
                  Configure your prospect details on the left, then click "Generate Prompt" to start a conversation with AI.
                </p>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <ChatBubble key={idx} message={msg} onQuickAction={handleQuickAction} />
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
                placeholder="Type your message..."
                disabled={loading || messages.length === 0}
                className="flex-1"
              />
              <Button 
                onClick={handleUserMessage}
                disabled={loading || !userInput.trim()}
                className="bg-indigo-600 hover:bg-indigo-700"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </Button>
            </div>
          </div>
        </div>

        {/* Prompt Preview Panel */}
        {promptPanelOpen && finalPrompt && (
          <div className="flex-shrink-0 w-96 border-l border-slate-200 bg-white flex flex-col">
            <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-white">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-indigo-600" />
                <h2 className="text-lg font-bold text-slate-900">Generated Prompt</h2>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setPromptPanelOpen(false)}
              >
                <X size={18} />
              </Button>
            </div>

            <div className="flex-1 overflow-y-auto p-4">
              <div className="bg-slate-50 rounded-lg p-4 font-mono text-xs whitespace-pre-wrap">
                {finalPrompt.prompt}
              </div>
            </div>

            <div className="p-4 border-t border-slate-200 space-y-2">
              <Button onClick={copyPrompt} className="w-full bg-indigo-600 hover:bg-indigo-700">
                <Copy className="w-4 h-4 mr-2" />
                Copy Prompt
              </Button>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

const ChatBubble = ({ message, onQuickAction }) => {
  const isUser = message.sender === 'user';
  const hasQuickActions = message.sender === 'assistant' && message.content.includes('Would you like me to');
  
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
        
        {hasQuickActions && onQuickAction && (
          <div className="flex flex-wrap gap-2 mt-2">
            <button
              onClick={() => onQuickAction('1')}
              className="px-3 py-1.5 text-xs font-medium bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              1. Generate Prompt
            </button>
            <button
              onClick={() => onQuickAction('2')}
              className="px-3 py-1.5 text-xs font-medium bg-slate-600 text-white rounded-lg hover:bg-slate-700"
            >
              2. Make Adjustments
            </button>
            <button
              onClick={() => onQuickAction('3')}
              className="px-3 py-1.5 text-xs font-medium bg-slate-600 text-white rounded-lg hover:bg-slate-700"
            >
              3. Add More Details
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default GTMGenerator;
