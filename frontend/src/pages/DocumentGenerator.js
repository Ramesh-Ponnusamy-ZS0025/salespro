import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { toast } from 'sonner';
import { FileText, Download } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Card } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DocumentGenerator = ({ user, onLogout }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [templateType, setTemplateType] = useState('nda');
  const [engagementModel, setEngagementModel] = useState('t&m');
  const [variables, setVariables] = useState({});

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${API}/documents`);
      setDocuments(response.data);
    } catch (error) {
      toast.error('Failed to fetch documents');
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API}/documents/generate`, {
        template_type: templateType,
        engagement_model: engagementModel,
        variables,
      });
      
      // Download the document
      const link = document.createElement('a');
      link.href = response.data.doc_url;
      link.download = `${templateType}_${Date.now()}.docx`;
      link.click();
      
      toast.success('Document generated successfully!');
      fetchDocuments();
      setVariables({});
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to generate document');
    } finally {
      setLoading(false);
    }
  };

  const renderNDAForm = () => (
    <>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>Party 1 Name *</Label>
          <Input
            data-testid="party1-name-input"
            value={variables.party1_name || ''}
            onChange={(e) => setVariables({ ...variables, party1_name: e.target.value })}
            placeholder="Company A Inc."
            required
          />
        </div>
        <div>
          <Label>Party 1 Short Name *</Label>
          <Input
            value={variables.party1_short || ''}
            onChange={(e) => setVariables({ ...variables, party1_short: e.target.value })}
            placeholder="Company A"
            required
          />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>Party 2 Name *</Label>
          <Input
            value={variables.party2_name || ''}
            onChange={(e) => setVariables({ ...variables, party2_name: e.target.value })}
            placeholder="Company B LLC"
            required
          />
        </div>
        <div>
          <Label>Party 2 Short Name *</Label>
          <Input
            value={variables.party2_short || ''}
            onChange={(e) => setVariables({ ...variables, party2_short: e.target.value })}
            placeholder="Company B"
            required
          />
        </div>
      </div>
      <div>
        <Label>Agreement Date *</Label>
        <Input
          type="date"
          value={variables.date || ''}
          onChange={(e) => setVariables({ ...variables, date: e.target.value })}
          required
        />
      </div>
      <div>
        <Label>Term Period *</Label>
        <Input
          value={variables.term || ''}
          onChange={(e) => setVariables({ ...variables, term: e.target.value })}
          placeholder="2 years from the date of signing"
          required
        />
      </div>
      <div>
        <Label>Confidential Information Description</Label>
        <Textarea
          value={variables.confidential_info || ''}
          onChange={(e) => setVariables({ ...variables, confidential_info: e.target.value })}
          placeholder="Technical specifications, business plans, customer data..."
          rows={3}
        />
      </div>
      <div>
        <Label>Obligations</Label>
        <Textarea
          value={variables.obligations || ''}
          onChange={(e) => setVariables({ ...variables, obligations: e.target.value })}
          placeholder="Both parties agree not to disclose..."
          rows={3}
        />
      </div>
    </>
  );

  const renderMSAForm = () => (
    <>
      <div>
        <Label>Client Name *</Label>
        <Input
          data-testid="client-name-input"
          value={variables.client_name || ''}
          onChange={(e) => setVariables({ ...variables, client_name: e.target.value })}
          placeholder="ABC Corporation"
          required
        />
      </div>
      <div>
        <Label>Service Provider Name *</Label>
        <Input
          value={variables.provider_name || ''}
          onChange={(e) => setVariables({ ...variables, provider_name: e.target.value })}
          placeholder="Your Company Inc."
          required
        />
      </div>
      <div>
        <Label>Effective Date *</Label>
        <Input
          type="date"
          value={variables.effective_date || ''}
          onChange={(e) => setVariables({ ...variables, effective_date: e.target.value })}
          required
        />
      </div>
      <div>
        <Label>Services Description *</Label>
        <Textarea
          value={variables.services_desc || ''}
          onChange={(e) => setVariables({ ...variables, services_desc: e.target.value })}
          placeholder="Software development, consulting, support services..."
          rows={3}
          required
        />
      </div>
      <div>
        <Label>Payment Terms</Label>
        <Textarea
          value={variables.payment_terms || ''}
          onChange={(e) => setVariables({ ...variables, payment_terms: e.target.value })}
          placeholder="Net 30 days from invoice date..."
          rows={2}
        />
      </div>
      <div>
        <Label>Term Period *</Label>
        <Input
          value={variables.term || ''}
          onChange={(e) => setVariables({ ...variables, term: e.target.value })}
          placeholder="12 months"
          required
        />
      </div>
    </>
  );

  const renderSOWForm = () => (
    <>
      <div>
        <Label>Project Name *</Label>
        <Input
          data-testid="project-name-input"
          value={variables.project_name || ''}
          onChange={(e) => setVariables({ ...variables, project_name: e.target.value })}
          placeholder="Digital Transformation Project"
          required
        />
      </div>
      <div>
        <Label>Client Name *</Label>
        <Input
          value={variables.client_name || ''}
          onChange={(e) => setVariables({ ...variables, client_name: e.target.value })}
          placeholder="ABC Corporation"
          required
        />
      </div>
      <div>
        <Label>Engagement Model *</Label>
        <Select value={engagementModel} onValueChange={setEngagementModel}>
          <SelectTrigger data-testid="engagement-model-select">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="t&m">Time & Materials</SelectItem>
            <SelectItem value="dedicated">Dedicated Team</SelectItem>
            <SelectItem value="fixed_bid">Fixed Bid</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div>
        <Label>Scope of Work *</Label>
        <Textarea
          value={variables.scope || ''}
          onChange={(e) => setVariables({ ...variables, scope: e.target.value })}
          placeholder="Project objectives, deliverables, milestones..."
          rows={4}
          required
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>Duration *</Label>
          <Input
            value={variables.duration || ''}
            onChange={(e) => setVariables({ ...variables, duration: e.target.value })}
            placeholder="6 months"
            required
          />
        </div>
        <div>
          <Label>Start Date *</Label>
          <Input
            type="date"
            value={variables.start_date || ''}
            onChange={(e) => setVariables({ ...variables, start_date: e.target.value })}
            required
          />
        </div>
      </div>
      <div>
        <Label>Resources</Label>
        <Textarea
          value={variables.resources || ''}
          onChange={(e) => setVariables({ ...variables, resources: e.target.value })}
          placeholder="2 Senior Developers, 1 Project Manager, 1 QA Engineer..."
          rows={2}
        />
      </div>
      <div>
        <Label>Total Cost *</Label>
        <Input
          type="number"
          value={variables.total_cost || ''}
          onChange={(e) => setVariables({ ...variables, total_cost: e.target.value })}
          placeholder="100000"
          required
        />
      </div>
      <div>
        <Label>Cost Breakdown</Label>
        <Textarea
          value={variables.cost_breakdown || ''}
          onChange={(e) => setVariables({ ...variables, cost_breakdown: e.target.value })}
          placeholder="Development: $70,000\nQA: $20,000\nManagement: $10,000"
          rows={3}
        />
      </div>
    </>
  );

  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="p-8" data-testid="document-generator-page">
        <div className="max-w-5xl mx-auto">
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-slate-900 mb-2">Document Generator</h1>
            <p className="text-slate-600">Generate professional legal documents with mail merge</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card className="p-6 bg-white border border-slate-200 shadow-lg">
                <Tabs value={templateType} onValueChange={setTemplateType}>
                  <TabsList className="grid grid-cols-3 mb-6">
                    <TabsTrigger value="nda" data-testid="nda-tab">NDA</TabsTrigger>
                    <TabsTrigger value="msa" data-testid="msa-tab">MSA</TabsTrigger>
                    <TabsTrigger value="sow" data-testid="sow-tab">SOW</TabsTrigger>
                  </TabsList>

                  <form onSubmit={handleGenerate} className="space-y-4">
                    <TabsContent value="nda">{renderNDAForm()}</TabsContent>
                    <TabsContent value="msa">{renderMSAForm()}</TabsContent>
                    <TabsContent value="sow">{renderSOWForm()}</TabsContent>

                    <div className="grid grid-cols-2 gap-4 pt-4">
                      <div>
                        <Label>Signatory 1 Name</Label>
                        <Input
                          value={variables.signatory1_name || ''}
                          onChange={(e) => setVariables({ ...variables, signatory1_name: e.target.value })}
                          placeholder="John Doe"
                        />
                      </div>
                      <div>
                        <Label>Signatory 1 Title</Label>
                        <Input
                          value={variables.signatory1_title || ''}
                          onChange={(e) => setVariables({ ...variables, signatory1_title: e.target.value })}
                          placeholder="CEO"
                        />
                      </div>
                      <div>
                        <Label>Signatory 2 Name</Label>
                        <Input
                          value={variables.signatory2_name || ''}
                          onChange={(e) => setVariables({ ...variables, signatory2_name: e.target.value })}
                          placeholder="Jane Smith"
                        />
                      </div>
                      <div>
                        <Label>Signatory 2 Title</Label>
                        <Input
                          value={variables.signatory2_title || ''}
                          onChange={(e) => setVariables({ ...variables, signatory2_title: e.target.value })}
                          placeholder="VP Operations"
                        />
                      </div>
                    </div>

                    <Button
                      type="submit"
                      disabled={loading}
                      data-testid="generate-document-button"
                      className="w-full mt-6"
                    >
                      {loading ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          Generating...
                        </>
                      ) : (
                        <>
                          <FileText size={18} className="mr-2" />
                          Generate Document
                        </>
                      )}
                    </Button>
                  </form>
                </Tabs>
              </Card>
            </div>

            <div>
              <Card className="p-6 bg-white border border-slate-200 shadow-lg">
                <h3 className="text-lg font-bold text-slate-900 mb-4">Recent Documents</h3>
                {documents.length > 0 ? (
                  <div className="space-y-3">
                    {documents.slice(0, 5).map((doc) => (
                      <div key={doc.id} className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="font-semibold text-sm text-slate-900">{doc.template_type.toUpperCase()}</p>
                            <p className="text-xs text-slate-600 mt-1">{doc.engagement_model}</p>
                          </div>
                          <Download size={16} className="text-indigo-600" />
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <FileText className="w-12 h-12 text-slate-300 mx-auto mb-2" />
                    <p className="text-sm text-slate-600">No documents yet</p>
                  </div>
                )}
              </Card>

              <Card className="p-6 bg-gradient-to-br from-indigo-50 to-blue-50 border border-indigo-100 mt-6">
                <h3 className="text-sm font-bold text-indigo-900 mb-2">Document Templates</h3>
                <ul className="text-xs text-indigo-700 space-y-1">
                  <li>• NDA - Non-Disclosure Agreement</li>
                  <li>• MSA - Master Service Agreement</li>
                  <li>• SOW - Statement of Work</li>
                </ul>
                <p className="text-xs text-indigo-600 mt-3">
                  All documents support mail merge fields and can be customized before generation.
                </p>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default DocumentGenerator;
