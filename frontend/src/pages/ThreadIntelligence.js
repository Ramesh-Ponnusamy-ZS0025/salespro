import React, { useState } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { toast } from 'sonner';
import { Sparkles, Mail, FileText } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Input } from '../components/ui/input';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ThreadIntelligence = ({ user, onLogout }) => {
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [threadText, setThreadText] = useState('');
  const [customInputs, setCustomInputs] = useState('');
  const [selectedCaseStudy, setSelectedCaseStudy] = useState('');

  // Mock case studies - in production, fetch from backend
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
      <div className="p-8" data-testid="thread-intelligence-page">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-slate-900 mb-2">Thread Intelligence</h1>
            <p className="text-slate-600">Analyze email threads and generate contextual follow-ups</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-6 bg-white border border-slate-200 shadow-lg">
              <h3 className="text-lg font-bold text-slate-900 mb-4">Paste Email Thread</h3>
              <div className="space-y-4">
                <div>
                  <Label>Email Thread Content *</Label>
                  <Textarea
                    data-testid="thread-input"
                    value={threadText}
                    onChange={(e) => setThreadText(e.target.value)}
                    placeholder="Paste your email thread here...\n\nFrom: John Doe\nTo: Jane Smith\nSubject: Product Demo\n\nHi Jane,\n\nThank you for the demo..."
                    rows={10}
                    className="font-mono text-sm"
                  />
                </div>
                <div>
                  <Label>Custom Inputs</Label>
                  <Textarea
                    data-testid="custom-inputs"
                    value={customInputs}
                    onChange={(e) => setCustomInputs(e.target.value)}
                    placeholder="Add any specific context, requirements, or notes that should be considered in the analysis..."
                    rows={3}
                  />
                </div>
                <div>
                  <Label>Select Relevant Case Study</Label>
                  <div className="border border-slate-200 rounded-md p-3 bg-white max-h-48 overflow-y-auto">
                    {caseStudies.map((caseStudy) => (
                      <div
                        key={caseStudy.id}
                        onClick={() => setSelectedCaseStudy(caseStudy.id)}
                        className={`p-3 mb-2 rounded-lg border-2 cursor-pointer transition-all ${
                          selectedCaseStudy === caseStudy.id
                            ? 'border-indigo-600 bg-indigo-50'
                            : 'border-slate-200 hover:border-indigo-300'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="font-semibold text-sm text-slate-900">{caseStudy.title}</p>
                            <p className="text-xs text-slate-600 mt-1">{caseStudy.industry}</p>
                          </div>
                          {selectedCaseStudy === caseStudy.id && (
                            <FileText size={16} className="text-indigo-600" />
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    {selectedCaseStudy ? 'Case study selected' : 'Optional: Select a relevant case study to reference'}
                  </p>
                </div>
                <Button
                  onClick={handleAnalyze}
                  disabled={loading}
                  data-testid="analyze-thread-button"
                  className="w-full"
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
            </Card>

            <div className="space-y-6">
              {analysis ? (
                <>
                  <Card className="p-6 bg-white border border-slate-200 shadow-lg">
                    <h3 className="text-lg font-bold text-slate-900 mb-4">Analysis Results</h3>
                    <div className="space-y-4">
                      <div>
                        <p className="text-sm font-semibold text-slate-700 mb-2">Summary:</p>
                        <p className="text-slate-800" data-testid="analysis-summary">{analysis.summary}</p>
                      </div>
                      <div className="flex gap-3">
                        <div>
                          <p className="text-sm font-semibold text-slate-700 mb-2">Stage:</p>
                          <Badge className={getStageColor(analysis.detected_stage)} data-testid="analysis-stage">
                            {analysis.detected_stage}
                          </Badge>
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-slate-700 mb-2">Sentiment:</p>
                          <Badge className={getSentimentColor(analysis.sentiment)} data-testid="analysis-sentiment">
                            {analysis.sentiment}
                          </Badge>
                        </div>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-slate-700 mb-2">Suggestions:</p>
                        <ul className="space-y-2">
                          {analysis.suggestions?.map((suggestion, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                              <span className="text-indigo-600 mt-1">•</span>
                              <span className="text-sm text-slate-700">{suggestion}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </Card>

                  {analysis.ai_followup && (
                    <Card className="p-6 bg-white border border-slate-200 shadow-lg">
                      <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
                        <Mail className="text-indigo-600" />
                        Suggested Follow-up
                      </h3>
                      <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                        <p className="text-slate-800 whitespace-pre-wrap" data-testid="followup-text">
                          {analysis.ai_followup}
                        </p>
                      </div>
                      <Button
                        onClick={() => {
                          navigator.clipboard.writeText(analysis.ai_followup);
                          toast.success('Follow-up copied to clipboard!');
                        }}
                        data-testid="copy-followup-button"
                        variant="outline"
                        className="w-full mt-4"
                      >
                        Copy Follow-up
                      </Button>
                    </Card>
                  )}
                </>
              ) : (
                <Card className="p-6 bg-white border border-slate-200 shadow-lg">
                  <div className="flex flex-col items-center justify-center h-[400px] text-center">
                    <Mail className="w-20 h-20 text-slate-300 mb-4" />
                    <h3 className="text-xl font-semibold text-slate-900 mb-2">No Analysis Yet</h3>
                    <p className="text-slate-600">Paste an email thread and click analyze to see results</p>
                  </div>
                </Card>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default ThreadIntelligence;