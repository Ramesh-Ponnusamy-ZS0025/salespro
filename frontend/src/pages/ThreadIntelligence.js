import React, { useState } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { toast } from 'sonner';
import { Sparkles, Mail, FileText, Check } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Card } from '../components/ui/card';
import {
  ResizablePanel,
  ResizablePanelGroup,
  ResizableHandle,
} from '../components/ui/resizable';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ThreadIntelligence = ({ user, onLogout }) => {
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [threadText, setThreadText] = useState('');
  const [customInputs, setCustomInputs] = useState('');
  const [selectedCaseStudy, setSelectedCaseStudy] = useState('');

  // Same case studies as before
  const caseStudies = [
    { id: '1', title: 'Enterprise Cloud Migration Success', industry: 'Technology' },
    { id: '2', title: 'AI Implementation for Healthcare', industry: 'Healthcare' },
    { id: '3', title: 'Digital Transformation in Finance', industry: 'Finance' },
    { id: '4', title: 'DevOps Automation Case Study', industry: 'Technology' },
    { id: '5', title: 'Quality Engineering Excellence', industry: 'Manufacturing' },
  ];

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
        case_study_id: selectedCaseStudy,
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
          <h1 className="text-3xl font-bold text-slate-900 mb-1">Thread Intelligence</h1>
          <p className="text-slate-600">
            Analyze email threads and generate contextual follow-ups
          </p>
        </div>

        {/* New Beautiful Split Layout */}
        <ResizablePanelGroup direction="horizontal" className="h-[calc(100%-120px)]">

          {/* LEFT PANEL — Your ORIGINAL input UI lives here */}
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

              {/* CASE STUDIES — Kept exactly as before */}
              <Card className="p-6 bg-white">
                <Label>Select Relevant Case Study</Label>
                <div className="border border-slate-200 rounded-md p-3 bg-white max-h-48 overflow-y-auto">
                  {caseStudies.map((cs) => (
                    <div
                      key={cs.id}
                      onClick={() => setSelectedCaseStudy(cs.id)}
                      className={`p-3 mb-2 rounded-lg border-2 cursor-pointer transition-all ${
                        selectedCaseStudy === cs.id
                          ? 'border-indigo-600 bg-indigo-50'
                          : 'border-slate-200 hover:border-indigo-300'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <p className="font-semibold text-sm text-slate-900">{cs.title}</p>
                          <p className="text-xs text-slate-600 mt-1">{cs.industry}</p>
                        </div>
                        {selectedCaseStudy === cs.id && (
                          <FileText size={16} className="text-indigo-600" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
                <p className="text-xs text-slate-500 mt-1">
                  {selectedCaseStudy ? 'Case study selected' : 'Optional: select a relevant case study'}
                </p>
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

          {/* RIGHT PANEL — Summary + Response */}
          <ResizablePanel defaultSize={60} minSize={40}>
            <div className="h-full overflow-y-auto p-8 bg-white">

              {!analysis ? (
                <div className="flex flex-col items-center justify-center h-96 text-center">
                  <Mail size={48} className="text-indigo-500 mb-4" />
                  <h3 className="text-lg font-semibold text-slate-900">
                    No Analysis Yet
                  </h3>
                  <p className="text-slate-600 mt-2 max-w-md">
                    Paste a thread and click “Analyze Thread” to see results.
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
