import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { toast } from 'sonner';
import { Sparkles, Mail, FileText } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Card } from '../components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import {
  ResizablePanel,
  ResizablePanelGroup,
  ResizableHandle,
} from '../components/ui/resizable';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Tone options - consistent with Agent Builder
const TONE_OPTIONS = [
  { value: 'professional', label: 'Professional', description: 'Formal, polished business communication. Respectful and direct.' },
  { value: 'data-driven', label: 'Data-Driven', description: 'Lead with metrics, ROI, quantifiable outcomes. Use specific numbers.' },
  { value: 'formal-human', label: 'Formal / Human', description: 'Professional yet personable. Balance formality with warmth.' },
  { value: 'cxo-pitch', label: 'CXO Pitch', description: 'Strategic, executive-level language. Address business priorities.' },
  { value: 'challenger-style', label: 'Challenger-Style', description: 'Challenge status quo. Teach, tailor, and take control.' },
  { value: 'basho-style', label: 'BASHO-Style', description: 'Build rapport first. Personalized, research-driven approach.' },
  { value: 'z-poet', label: 'Z Poet', description: 'Creative, memorable messaging with metaphors and storytelling.' },
  { value: 'urgency-framing', label: 'Urgency-Framing', description: 'Create time-sensitive value. Emphasize FOMO and immediate benefits.' },
  { value: 'executive-briefing', label: 'Executive Briefing', description: 'Concise, high-level strategic communication. Bottom-line focused.' },
  { value: 'casual', label: 'Casual', description: 'Conversational and approachable. Friendly tone while maintaining respect.' },
  { value: 'friendly', label: 'Friendly', description: 'Warm and personable. Build connection through empathy.' },
  { value: 'authoritative', label: 'Authoritative', description: 'Confident and expert-driven. Establish credibility and thought leadership.' },
  { value: 'consultative', label: 'Consultative', description: 'Advisory approach. Position as trusted partner offering solutions.' },
  { value: 'concise', label: 'Concise', description: 'Brief, direct messaging. Clear value proposition in minimal words.' },
];

const ThreadIntelligence = ({ user, onLogout }) => {
  const [loading, setLoading] = useState(false);
  const [loadingFiles, setLoadingFiles] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [threadText, setThreadText] = useState('');
  const [customInputs, setCustomInputs] = useState('');
  const [selectedTone, setSelectedTone] = useState('professional');
  const [selectedCaseStudies, setSelectedCaseStudies] = useState([]);
  const [autoPickCaseStudies, setAutoPickCaseStudies] = useState(true);
  const [availableDocuments, setAvailableDocuments] = useState([]);

  useEffect(() => {
    fetchAvailableDocuments();
  }, []);

  // Fetch available documents/case studies - consistent with Campaign Builder
  const fetchAvailableDocuments = async () => {
    try {
      const response = await axios.get(`${API}/document-files/for-campaign`);
      setAvailableDocuments(response.data.documents || []);
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    }
  };

  const toggleCaseStudy = (docId) => {
    setSelectedCaseStudies(prev =>
      prev.includes(docId)
        ? prev.filter(id => id !== docId)
        : [...prev, docId]
    );
  };

  const handleAnalyze = async () => {
    if (!threadText.trim()) {
      toast.error('Please paste an email thread');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/thread/analyze`, {
        thread_text: threadText,
        custom_inputs: customInputs,
        tone: selectedTone,
        selected_case_studies: selectedCaseStudies,
        auto_pick_case_studies: autoPickCaseStudies,
      });

      setAnalysis(response.data);
      toast.success('Thread analyzed successfully!');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to analyze thread');
    } finally {
      setLoading(false);
    }
  };

  const copyResponse = () => {
    if (analysis?.response) {
      navigator.clipboard.writeText(analysis.response);
      toast.success('Response copied!');
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return 'bg-green-100 text-green-700';
      case 'negative':
        return 'bg-red-100 text-red-700';
      default:
        return 'bg-slate-100 text-slate-700';
    }
  };

  const getStageColor = (stage) => {
    switch (stage?.toLowerCase()) {
      case 'hot':
        return 'bg-red-100 text-red-700';
      case 'warm':
        return 'bg-yellow-100 text-yellow-700';
      default:
        return 'bg-blue-100 text-blue-700';
    }
  };

  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="h-[calc(100vh-4rem)]">

        {/* Header */}
        <div className="px-8 pt-6 pb-4 border-b border-slate-200 bg-white">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 mb-1">Thread Intelligence</h1>
              <p className="text-slate-600">
                Analyze email threads and generate contextual follow-ups
              </p>
            </div>
          </div>
        </div>

        {/* Split Layout */}
        <ResizablePanelGroup direction="horizontal" className="h-[calc(100%-120px)]">

          {/* LEFT PANEL */}
          <ResizablePanel defaultSize={40} minSize={30}>
            <div className="h-full overflow-y-auto p-8 bg-slate-50 space-y-6">

              {/* THREAD INPUT */}
              <Card className="p-6 bg-white">
                <Label>Email Thread Content *</Label>
                <Textarea
                  value={threadText}
                  onChange={(e) => setThreadText(e.target.value)}
                  placeholder="Paste your email thread here..."
                  rows={10}
                  className="font-mono text-sm"
                />
              </Card>

              {/* CUSTOM INPUTS */}
              <Card className="p-6 bg-white">
                <Label>Custom Inputs</Label>
                <Textarea
                  value={customInputs}
                  onChange={(e) => setCustomInputs(e.target.value)}
                  placeholder="Add your draft notes or reply intent..."
                  rows={3}
                />
              </Card>

              {/* TONE SELECTION - Dropdown */}
              <Card className="p-6 bg-white">
                <Label className="text-sm font-medium mb-3 block">Response Tone</Label>
                <Select value={selectedTone} onValueChange={setSelectedTone}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select tone" />
                  </SelectTrigger>
                  <SelectContent>
                    {TONE_OPTIONS.map((tone) => (
                      <SelectItem key={tone.value} value={tone.value}>
                        {tone.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-slate-500 mt-2">
                  {TONE_OPTIONS.find(t => t.value === selectedTone)?.description}
                </p>
              </Card>

              {/* CASE STUDIES - Consistent with Campaign Builder */}
              <Card className="p-6 bg-white">
                <div className="flex items-center justify-between mb-2">
                  <Label className="text-sm font-medium">Case Studies & Documents</Label>
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="auto-pick-cs"
                      checked={autoPickCaseStudies}
                      onChange={(e) => {
                        setAutoPickCaseStudies(e.target.checked);
                        if (e.target.checked) {
                          setSelectedCaseStudies([]);
                        }
                      }}
                      className="rounded"
                    />
                    <label htmlFor="auto-pick-cs" className="cursor-pointer text-sm">
                      Auto Pick
                    </label>
                  </div>
                </div>

                {!autoPickCaseStudies && (
                  <div className="border rounded-lg p-3 max-h-48 overflow-y-auto space-y-2 bg-white">
                    {availableDocuments.length === 0 ? (
                      <p className="text-sm text-slate-500">No documents available</p>
                    ) : (
                      availableDocuments.map(doc => (
                        <div
                          key={doc.id}
                          className="flex items-start gap-2 p-2 hover:bg-slate-50 rounded cursor-pointer"
                          onClick={() => toggleCaseStudy(doc.id)}
                        >
                          <input
                            type="checkbox"
                            checked={selectedCaseStudies.includes(doc.id)}
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

                {autoPickCaseStudies && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800">
                    ✨ Case studies will be automatically selected based on thread context
                  </div>
                )}
              </Card>

              {/* ANALYZE BUTTON */}
              <Button
                onClick={handleAnalyze}
                disabled={loading}
                className="w-full bg-indigo-600 hover:bg-indigo-700 py-6 text-lg"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Sparkles size={18} className="mr-2" />
                    Analyze Thread
                  </>
                )}
              </Button>

            </div>
          </ResizablePanel>

          <ResizableHandle withHandle />

          {/* RIGHT PANEL */}
          <ResizablePanel defaultSize={60} minSize={40}>
            <div className="h-full overflow-y-auto p-8 bg-white">

              {!analysis ? (
                <div className="flex flex-col items-center justify-center h-96 text-center">
                  <Mail size={48} className="text-indigo-500 mb-4" />
                  <h3 className="text-lg font-semibold text-slate-900">
                    No Analysis Yet
                  </h3>
                  <p className="text-slate-600 mt-2 max-w-md">
                    Paste a thread and click "Analyze Thread" to see results.
                  </p>
                </div>
              ) : (
                <div className="space-y-6 max-w-4xl mx-auto">

                  {/* SUMMARY SECTION */}
                  <Card className="p-6 bg-white border border-slate-200">
                    <h3 className="text-lg font-semibold text-slate-900 mb-3">Summary</h3>
                    <p className="text-slate-800">{analysis.summary}</p>

                    <div className="flex gap-4 mt-4">
                      <span className={`px-3 py-1 rounded text-sm ${getStageColor(analysis.detected_stage)}`}>
                        {analysis.detected_stage}
                      </span>
                      <span className={`px-3 py-1 rounded text-sm ${getSentimentColor(analysis.sentiment)}`}>
                        {analysis.sentiment}
                      </span>
                    </div>
                  </Card>

                  {/* RESPONSE SECTION */}
                  <Card className="p-6 bg-gradient-to-br from-slate-50 to-indigo-50 border border-indigo-200">
                    <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
                      <FileText size={18} className="text-indigo-600" />
                      Suggested Response
                    </h3>

                    <div className="bg-white p-5 rounded border border-slate-200">
                      <pre className="whitespace-pre-wrap text-slate-900">
                        {analysis.response}
                      </pre>
                    </div>

                    <Button
                      onClick={copyResponse}
                      variant="outline"
                      className="mt-4 w-full"
                    >
                      Copy Response
                    </Button>
                  </Card>

                </div>
              )}
            </div>
          </ResizablePanel>

        </ResizablePanelGroup>

      </div>
    </Layout>
  );
};

export default ThreadIntelligence;
