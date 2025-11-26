import React, { useState, useEffect, useRef } from 'react';
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
import { renderAsync } from 'docx-preview';
//import 'docx-preview/dist/docx-preview.css';


const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DocumentGenerator = ({ user, onLogout }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [templateType, setTemplateType] = useState('nda');
  const [engagementModel, setEngagementModel] = useState('t&m');
  const [variables, setVariables] = useState({});
  const [showDocxModal, setShowDocxModal] = useState(false);
  const [currentDocBase64, setCurrentDocBase64] = useState('');
  const previewRef = useRef(null);

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
      if (templateType === 'msa') {
        response = await axios.post(`${API}/documents/msa/generate`, variables);
      } else {
        response = await axios.post(`${API}/documents/generate`, {
          template_type: templateType,
          engagement_model: engagementModel,
          variables,
        });
      }

      // Convert base64 to Blob
      const byteCharacters = atob(response.data.doc_base64);
      const byteNumbers = Array.from(byteCharacters, char => char.charCodeAt(0));
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], {
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      });

      // Preview DOCX
      setCurrentDocBase64(response.data.doc_base64);
      setShowDocxModal(true);
      
      // Wait for modal to render, then show preview
      setTimeout(async () => {
        try {
          const arrayBuffer = await blob.arrayBuffer();
          if (previewRef.current) {
            previewRef.current.innerHTML = ''; // clear previous
            await renderAsync(arrayBuffer, previewRef.current, null, {
              className: 'docx-wrapper',
              inWrapper: true,
              ignoreWidth: false,
              ignoreHeight: false,
              renderHeaders: true,
              renderFooters: true,
              useBase64URL: false,
            });
            console.log('DOCX rendered successfully');
          }
        } catch (err) {
          console.error('Error rendering DOCX:', err);
          toast.error('Failed to render document preview');
        }
      }, 100);
      toast.success(response.data.message || 'Document generated successfully!');
      fetchDocuments();
      setVariables({});
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to generate document');
    } finally {
      setLoading(false);
    }
  };

  // ---------------- Forms ----------------
  const renderNDAForm = () => (
    <>
      <div>
        <Label>Date *</Label>
        <Input
          type="date"
          value={variables.date || ''}
          onChange={(e) => setVariables({ ...variables, date: e.target.value })}
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
          placeholder="2 Senior Developers, 1 Project Manager..."
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

  // ---------------- Main JSX ----------------
  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="p-8">
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
                    <TabsTrigger value="nda">NDA</TabsTrigger>
                    <TabsTrigger value="msa">MSA</TabsTrigger>
                    <TabsTrigger value="sow">SOW</TabsTrigger>
                  </TabsList>

                  <form onSubmit={handleGenerate} className="space-y-4">
                    <TabsContent value="nda">{renderNDAForm()}</TabsContent>
                    <TabsContent value="msa">{renderMSAForm()}</TabsContent>
                    <TabsContent value="sow">{renderSOWForm()}</TabsContent>

                    <Button type="submit" disabled={loading} className="w-full mt-6">
                      {loading ? 'Generating...' : (
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
                {documents.length ? (
                  <div className="space-y-3">
                    {documents.slice(0, 5).map(doc => (
                      <div key={doc.id} className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex justify-between items-center">
                        <div>
                          <p className="font-semibold text-sm">{doc.template_type.toUpperCase()}</p>
                          <p className="text-xs text-slate-600">{doc.engagement_model}</p>
                        </div>
                        <Download
                          size={16}
                          className="text-indigo-600 cursor-pointer"
                          onClick={() => {
                            if (doc.doc_base64) {
                              const byteCharacters = atob(doc.doc_base64);
                              const byteNumbers = Array.from(byteCharacters, char => char.charCodeAt(0));
                              const byteArray = new Uint8Array(byteNumbers);
                              const blob = new Blob([byteArray], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
                              const link = document.createElement('a');
                              link.href = URL.createObjectURL(blob);
                              link.download = `${doc.template_type}_${Date.now()}.docx`;
                              link.click();
                            }
                          }}
                        />
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-600 text-center">No documents yet</p>
                )}
              </Card>
            </div>
          </div>
        </div>

        {/* DOCX Preview Modal */}
        {showDocxModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-2xl w-full max-w-5xl h-[90vh] flex flex-col">
              <div className="flex items-center justify-between p-4 border-b">
                <h3 className="text-xl font-bold">Document Preview</h3>
                <div className="flex gap-2">
                  <Button
                    onClick={() => {
                      if (currentDocBase64) {
                        const byteCharacters = atob(currentDocBase64);
                        const byteNumbers = Array.from(byteCharacters, char => char.charCodeAt(0));
                        const byteArray = new Uint8Array(byteNumbers);
                        const blob = new Blob([byteArray], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
                        const link = document.createElement('a');
                        link.href = URL.createObjectURL(blob);
                        link.download = `${templateType}_${Date.now()}.docx`;
                        link.click();
                      }
                    }}
                    variant="outline"
                    size="sm"
                  >
                    <Download size={16} className="mr-2" />
                    Download DOCX
                  </Button>
                  <Button onClick={() => setShowDocxModal(false)} variant="outline" size="sm">
                    Close
                  </Button>
                </div>
              </div>
              <div className="flex-1 overflow-auto p-4 bg-gray-50">
                <div ref={previewRef} className="docx-wrapper" style={{ minHeight: '500px', background: 'white', padding: '20px' }} />
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default DocumentGenerator;
