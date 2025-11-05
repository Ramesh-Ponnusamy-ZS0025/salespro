import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { toast } from 'sonner';
import { FileText, Download } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
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
  const [pdfPreview, setPdfPreview] = useState(null);
  const [showPdfModal, setShowPdfModal] = useState(false);

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
      let response;
      
      // Use new MSA endpoint for MSA documents
      if (templateType === 'msa') {
        response = await axios.post(`${API}/documents/msa/generate`, variables);
      } else {
        response = await axios.post(`${API}/documents/generate`, {
          template_type: templateType,
          engagement_model: engagementModel,
          variables,
        });
      }
      
      // Download DOCX
      const docxLink = document.createElement('a');
      docxLink.href = response.data.doc_url;
      docxLink.download = `${templateType}_${Date.now()}.docx`;
      docxLink.click();
      
      // Download PDF if available and show preview
      if (response.data.pdf_url) {
        setPdfPreview(response.data.pdf_url);
        setShowPdfModal(true);
        
        setTimeout(() => {
          const pdfLink = document.createElement('a');
          pdfLink.href = response.data.pdf_url;
          pdfLink.download = `${templateType}_${Date.now()}.pdf`;
          pdfLink.click();
        }, 500);
      }
      
      toast.success(response.data.message || 'Document generated successfully!');
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
      <div>
        <Label>Date *</Label>
        <Input
          type="date"
          data-testid="nda-date-input"
          value={variables.date || ''}
          onChange={(e) => setVariables({ ...variables, date: e.target.value })}
          required
        />
      </div>
      <div>
        <Label>Customer Company Name *</Label>
        <Input
          value={variables.customer_company_name || ''}
          onChange={(e) => setVariables({ ...variables, customer_company_name: e.target.value })}
          placeholder="ABC Corporation"
          required
        />
      </div>
      <div>
        <Label>Customer Company Address *</Label>
        <Textarea
          value={variables.customer_company_address || ''}
          onChange={(e) => setVariables({ ...variables, customer_company_address: e.target.value })}
          placeholder="123 Business St, Suite 100, City, State 12345"
          rows={2}
          required
        />
      </div>
      <div>
        <Label>Title *</Label>
        <Input
          value={variables.title || ''}
          onChange={(e) => setVariables({ ...variables, title: e.target.value })}
          placeholder="CEO"
          required
        />
      </div>
      <div>
        <Label>Name *</Label>
        <Input
          value={variables.name || ''}
          onChange={(e) => setVariables({ ...variables, name: e.target.value })}
          placeholder="John Doe"
          required
        />
      </div>
    </>
  );

  const renderMSAForm = () => (
    <>
      <div>
        <Label>Date *</Label>
        <Input
          type="date"
          data-testid="msa-date-input"
          value={variables.date || ''}
          onChange={(e) => setVariables({ ...variables, date: e.target.value })}
          required
        />
      </div>
      <div>
        <Label>Company Name *</Label>
        <Input
          value={variables.company_name || ''}
          onChange={(e) => setVariables({ ...variables, company_name: e.target.value })}
          placeholder="Your Company Inc."
          required
        />
      </div>
      <div>
        <Label>Customer Company Address *</Label>
        <Textarea
          value={variables.customer_company_address || ''}
          onChange={(e) => setVariables({ ...variables, customer_company_address: e.target.value })}
          placeholder="123 Business St, Suite 100, City, State 12345"
          rows={2}
          required
        />
      </div>
      <div>
        <Label>Point of Contact *</Label>
        <Input
          value={variables.point_of_contact || ''}
          onChange={(e) => setVariables({ ...variables, point_of_contact: e.target.value })}
          placeholder="Jane Smith"
          required
        />
      </div>
      <div>
        <Label>Customer Company Name *</Label>
        <Input
          value={variables.customer_company_name || ''}
          onChange={(e) => setVariables({ ...variables, customer_company_name: e.target.value })}
          placeholder="ABC Corporation"
          required
        />
      </div>
      <div>
        <Label>Title *</Label>
        <Input
          value={variables.title || ''}
          onChange={(e) => setVariables({ ...variables, title: e.target.value })}
          placeholder="VP Operations"
          required
        />
      </div>
      <div>
        <Label>Name *</Label>
        <Input
          value={variables.name || ''}
          onChange={(e) => setVariables({ ...variables, name: e.target.value })}
          placeholder="John Doe"
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

      {/* PDF Preview Modal */}
      {showPdfModal && pdfPreview && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-2xl w-full max-w-5xl h-[90vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-xl font-bold text-slate-900">Document Preview</h3>
              <div className="flex gap-2">
                <Button
                  onClick={() => {
                    const link = document.createElement('a');
                    link.href = pdfPreview;
                    link.download = `${templateType}_${Date.now()}.pdf`;
                    link.click();
                  }}
                  variant="outline"
                  size="sm"
                >
                  <Download size={16} className="mr-2" />
                  Download PDF
                </Button>
                <Button
                  onClick={() => setShowPdfModal(false)}
                  variant="outline"
                  size="sm"
                >
                  Close
                </Button>
              </div>
            </div>
            <div className="flex-1 overflow-auto">
              <iframe
                src={pdfPreview}
                className="w-full h-full"
                title="PDF Preview"
              />
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
};

export default DocumentGenerator;