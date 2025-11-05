import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { toast } from 'sonner';
import {
  Link2, MessageSquare, Sparkles, Copy, RefreshCw,
  Check, Wand2, FileText, User
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Card } from '../components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '../components/ui/resizable';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const INPUT_MODES = {
  URL: 'url',
  MESSAGE: 'message'
};

const TONES = [
  { value: 'professional', label: 'Professional' },
  { value: 'friendly', label: 'Friendly' },
  { value: 'enthusiastic', label: 'Enthusiastic' },
  { value: 'casual', label: 'Casual' },
  { value: 'formal', label: 'Formal' },
];

const LENGTHS = [
  { value: 'short', label: 'Short (50-100 words)' },
  { value: 'medium', label: 'Medium (100-200 words)' },
  { value: 'long', label: 'Long (200-300 words)' },
];

const STYLES = [
  { value: 'linkedin', label: 'LinkedIn Message' },
  { value: 'email', label: 'Email Copy' },
  { value: 'cold_email', label: 'Cold Email' },
  { value: 'follow_up', label: 'Follow-up Message' },
];

const PersonalizationAssistant = ({ user, onLogout }) => {
//  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);

  // Input mode state
  const [inputMode, setInputMode] = useState(INPUT_MODES.URL);
  const [customMessage, setCustomMessage] = useState('');
  const [tone, setTone] = useState('professional');
  const [length, setLength] = useState('medium');
  const [style, setStyle] = useState('linkedin');

  // Generated message state
  const [generatedMessage, setGeneratedMessage] = useState(null);



  const [formData, setFormData] = useState({
    origin_url: '',
    keywords: '',
    custom_input: '',
  });




  const handleGenerate = async () => {
    // Validation
    if (inputMode === INPUT_MODES.URL && !formData.origin_url.trim()) {
      toast.error('Please provide a URL');
      return;
    }

    if (inputMode === INPUT_MODES.MESSAGE && !customMessage.trim()) {
      toast.error('Please write your message');
      return;
    }



    setGenerating(true);

    const payload = {
      origin_url: inputMode === INPUT_MODES.URL ? formData.origin_url : 'custom_message',

      keywords: formData.keywords.split(',').map(k => k.trim()).filter(Boolean),
      notes: inputMode === INPUT_MODES.MESSAGE
        ? `${formData.custom_input}\n\nBase message: ${customMessage}\nTone: ${tone}\nLength: ${length}\nStyle: ${style}`
        : formData.custom_input,
//      sender_profile: userProfile,
    };

    try {
      const response = await axios.post(`${API}/personalize/generate`, payload);
      setGeneratedMessage(response.data);
      toast.success('Personalized message generated!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to generate message');
    } finally {
      setGenerating(false);
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
      <div className="h-[calc(100vh-4rem)]">
        {/* Header */}
        <div className="px-8 pt-6 pb-4 border-b border-slate-200 bg-white">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 mb-1">
                Personalization Assistant
              </h1>
              <p className="text-slate-600">
                Generate personalized 1:1 outreach messages with AI
              </p>
            </div>
            <div className="flex gap-2">
              {generatedMessage && (
                <>
                  <Button variant="outline" onClick={copyToClipboard} data-testid="copy-message-button">
                    <Copy size={16} className="mr-2" /> Copy Message
                  </Button>
                  <Button onClick={handleGenerate} disabled={generating}>
                    <RefreshCw size={16} className="mr-2" /> Regenerate
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Split Layout */}
        <ResizablePanelGroup direction="horizontal" className="h-[calc(100%-120px)]">
          {/* Left Panel - Configuration */}
          <ResizablePanel defaultSize={35} minSize={30}>
            <div className="h-full overflow-y-auto p-8 bg-slate-50">
              <div className="max-w-2xl">
                <h2 className="text-xl font-bold text-slate-900 mb-6">
                  Configuration
                </h2>

                <div className="space-y-6">
                  {/* User Profile Section */}


                  {/* Input Mode Selection */}
                  <Card className="p-6 bg-white">
                    <Label className="text-lg font-semibold mb-4 block">
                      Choose Input Type
                    </Label>
                    <div className="grid grid-cols-2 gap-3">
                      <Card
                        onClick={() => setInputMode(INPUT_MODES.URL)}
                        className={`p-4 cursor-pointer transition-all ${
                          inputMode === INPUT_MODES.URL
                            ? 'bg-gradient-to-br from-indigo-50 to-blue-50 border-2 border-indigo-600'
                            : 'bg-white border border-slate-200 hover:border-indigo-300'
                        }`}
                      >
                        <div className="flex flex-col items-center text-center gap-2">
                          <Link2 size={24} className={inputMode === INPUT_MODES.URL ? 'text-indigo-600' : 'text-slate-400'} />
                          <span className="font-semibold text-sm">LinkedIn / Company URL</span>
                        </div>
                      </Card>

                      <Card
                        onClick={() => setInputMode(INPUT_MODES.MESSAGE)}
                        className={`p-4 cursor-pointer transition-all ${
                          inputMode === INPUT_MODES.MESSAGE
                            ? 'bg-gradient-to-br from-indigo-50 to-blue-50 border-2 border-indigo-600'
                            : 'bg-white border border-slate-200 hover:border-indigo-300'
                        }`}
                      >
                        <div className="flex flex-col items-center text-center gap-2">
                          <FileText size={24} className={inputMode === INPUT_MODES.MESSAGE ? 'text-indigo-600' : 'text-slate-400'} />
                          <span className="font-semibold text-sm">Write Your Own</span>
                        </div>
                      </Card>
                    </div>
                  </Card>

                  {/* URL Mode */}
                  {inputMode === INPUT_MODES.URL && (
                    <Card className="p-6 bg-white">
                      <Label className="text-lg font-semibold mb-4 block">
                        LinkedIn or Company URL
                      </Label>
                      <Input
                        type="url"
                        data-testid="origin-url-input"
                        value={formData.origin_url}
                        onChange={(e) => setFormData({ ...formData, origin_url: e.target.value })}
                        placeholder="https://linkedin.com/in/..."
                        className="mb-2"
                      />
                      <p className="text-xs text-slate-600">
                        💡 We'll analyze the profile or company to personalize your message
                      </p>
                    </Card>
                  )}

                  {/* Message Mode */}
                  {inputMode === INPUT_MODES.MESSAGE && (
                    <Card className="p-6 bg-white space-y-4">
                      <div>
                        <Label className="text-lg font-semibold mb-4 block">
                          Your Draft Message
                        </Label>
                        <Textarea
                          value={customMessage}
                          onChange={(e) => setCustomMessage(e.target.value)}
                          placeholder="Write or paste your initial message here..."
                          rows={6}
                          className="mb-2"
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label className="text-sm mb-2 block">Tone</Label>
                          <Select value={tone} onValueChange={setTone}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {TONES.map((t) => (
                                <SelectItem key={t.value} value={t.value}>
                                  {t.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>

                        <div>
                          <Label className="text-sm mb-2 block">Length</Label>
                          <Select value={length} onValueChange={setLength}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {LENGTHS.map((l) => (
                                <SelectItem key={l.value} value={l.value}>
                                  {l.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      </div>

                      <div>
                        <Label className="text-sm mb-2 block">Style</Label>
                        <Select value={style} onValueChange={setStyle}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {STYLES.map((s) => (
                              <SelectItem key={s.value} value={s.value}>
                                {s.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </Card>
                  )}

                  {/* Agent Selection */}


                  {/* Optional Fields */}
                  <Card className="p-6 bg-white space-y-4">
                    <Label className="text-lg font-semibold block">
                      Additional Details (Optional)
                    </Label>

                    <div>
                      <Label className="text-sm mb-2 block">Keywords</Label>
                      <Input
                        value={formData.keywords}
                        onChange={(e) => setFormData({ ...formData, keywords: e.target.value })}
                        placeholder="innovation, growth, transformation (comma-separated)"
                      />
                      <p className="text-xs text-slate-600 mt-1">
                        Add relevant keywords to focus the message
                      </p>
                    </div>

                    <div>
                      <Label className="text-sm mb-2 block">Additional Notes</Label>
                      <Textarea
                        value={formData.custom_input}
                        onChange={(e) => setFormData({ ...formData, custom_input: e.target.value })}
                        placeholder="Any specific instructions or context..."
                        rows={3}
                      />
                    </div>
                  </Card>

                  {/* Generate Button */}
                  <Button
                    onClick={handleGenerate}
                    disabled={generating || loading}
                    data-testid="generate-message-button"
                    className="w-full bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 py-6 text-lg"
                  >
                    {generating ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Generating...
                      </>
                    ) : (
                      <>
                        <Sparkles size={20} className="mr-2" />
                        Generate Personalized Message
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </div>
          </ResizablePanel>

          <ResizableHandle withHandle />

          {/* Right Panel - Output Preview */}
          <ResizablePanel defaultSize={65} minSize={40}>
            <div className="h-full overflow-y-auto p-8 bg-white">
              <div className="max-w-4xl mx-auto">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-slate-900">
                    Generated Message
                  </h2>
                  {generatedMessage && (
                    <div className="flex items-center gap-2 text-sm text-slate-600">
                      <span>{generatedMessage.char_count} characters</span>
                      <span>•</span>
                      <span className="text-green-600 flex items-center gap-1">
                        <Check size={14} />
                        Ready
                      </span>
                    </div>
                  )}
                </div>

                {!generatedMessage ? (
                  <div className="flex flex-col items-center justify-center h-96 text-center">
                    <div className="w-20 h-20 bg-gradient-to-br from-indigo-100 to-blue-100 rounded-full flex items-center justify-center mb-6">
                      <MessageSquare size={40} className="text-indigo-600" />
                    </div>
                    <h3 className="text-lg font-semibold text-slate-900 mb-2">
                      No message generated yet
                    </h3>
                    <p className="text-slate-600 max-w-md">
                      Start by configuring personalization options on the left panel and click "Generate Personalized Message"
                    </p>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {/* Message Preview */}
                    <Card className="p-6 bg-gradient-to-br from-slate-50 to-blue-50 border-2 border-indigo-200">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-2">
                          <div className="w-10 h-10 bg-indigo-600 rounded-lg flex items-center justify-center">
                            <Wand2 className="text-white" size={20} />
                          </div>
                          <div>
                            <h3 className="font-semibold text-slate-900">
                              Personalized {style === 'linkedin' ? 'LinkedIn Message' :
                                         style === 'email' ? 'Email Copy' :
                                         style === 'cold_email' ? 'Cold Email' :
                                         'Follow-up Message'}
                            </h3>
                            <p className="text-xs text-slate-600">
                              AI-generated • ID: {generatedMessage.id.slice(0, 8)}
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="bg-white p-6 rounded-lg border border-slate-200 mb-4">
                        <pre className="whitespace-pre-wrap font-sans text-slate-800 leading-relaxed" data-testid="generated-message">
                          {generatedMessage.message}
                        </pre>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex gap-2">
                        <Button
                          onClick={copyToClipboard}
                          variant="outline"
                          className="flex-1"
                        >
                          <Copy size={16} className="mr-2" />
                          Copy to Clipboard
                        </Button>
                        <Button
                          onClick={handleGenerate}
                          disabled={generating}
                          className="flex-1 bg-indigo-600 hover:bg-indigo-700"
                        >
                          {generating ? (
                            <>
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                              Regenerating...
                            </>
                          ) : (
                            <>
                              <RefreshCw size={16} className="mr-2" />
                              Regenerate
                            </>
                          )}
                        </Button>
                      </div>
                    </Card>

                    {/* Tips Section */}
                    <Card className="p-6 bg-blue-50 border border-blue-200">
                      <h4 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
                        <Sparkles size={16} />
                        Tips for Best Results
                      </h4>
                      <ul className="space-y-2 text-sm text-blue-800">
                        <li className="flex items-start gap-2">
                          <Check size={16} className="mt-0.5 flex-shrink-0" />
                          <span>Review and personalize the message before sending</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <Check size={16} className="mt-0.5 flex-shrink-0" />
                          <span>Add specific details about the recipient or their company</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <Check size={16} className="mt-0.5 flex-shrink-0" />
                          <span>Keep the tone consistent with your brand voice</span>
                        </li>
                        <li className="flex items-start gap-2">
                          <Check size={16} className="mt-0.5 flex-shrink-0" />
                          <span>Test different variations to see what resonates</span>
                        </li>
                      </ul>
                    </Card>
                  </div>
                )}
              </div>
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    </Layout>
  );
};

export default PersonalizationAssistant;