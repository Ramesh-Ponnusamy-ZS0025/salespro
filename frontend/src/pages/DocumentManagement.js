import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { toast } from 'sonner';
import {
  FileText, Upload, Download, Trash2, ChevronDown, ChevronRight,
  File, FileImage, Search, Plus, X, Edit2, Check, Loader, Globe
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '../components/ui/resizable';
import { renderAsync } from 'docx-preview';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CATEGORIES = [
  'Healthcare',
  'Finance',
  'E-commerce',
  'Manufacturing',
  'Retail',
  'Technology',
  'Education',
  'Real Estate',
  'Logistics',
  'Telecommunications',
  'AI'
];

const DOC_TYPES = [
  'Case Study',
  'Architecture',
  'Use Case',
  'Design',
  'Figma',
  'Workflow',
  'Presentation',
  'Report',
  'Whitepaper',
  'Industry Solution',
  'Transformation Story'
];

const SUPPORTED_FORMATS = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'image/png',
  'image/jpeg',
  'image/jpg'
];

const DocumentManagement = ({ user, onLogout }) => {
  const [documents, setDocuments] = useState([]);
  const [groupedDocs, setGroupedDocs] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [expandedCategories, setExpandedCategories] = useState({});
  const [expandedTypes, setExpandedTypes] = useState({});
  const [searchQuery, setSearchQuery] = useState('');
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [renderingDocx, setRenderingDocx] = useState(false);
  const [docxRenderKey, setDocxRenderKey] = useState(0);
  const [docxHtml, setDocxHtml] = useState('');
  const [scrapingZuci, setScrapingZuci] = useState(false);
  const [pdfError, setPdfError] = useState(false);
  const [useEmbedForPdf, setUseEmbedForPdf] = useState(false);
  const [pdfBlobUrl, setPdfBlobUrl] = useState(null);

  const [uploadForm, setUploadForm] = useState({
    category: '',
    doc_type: '',
    file: null
  });

  useEffect(() => {

    fetchDocuments();
  }, []);

  useEffect(() => {
    
    // Cleanup function to revoke Blob URLs when component unmounts
    return () => {
      if (pdfBlobUrl) {
        URL.revokeObjectURL(pdfBlobUrl);
      }
    };
  }, [pdfBlobUrl]);

  useEffect(() => {
    // Render DOCX when selectedDoc changes and it's a DOCX file
    if (selectedDoc && 
        selectedDoc.mime_type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' &&
        !renderingDocx) {
      renderDocxPreview(selectedDoc.file_content);
    }
  }, [selectedDoc]);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/document-files`);
      setDocuments(response.data.documents);
      setGroupedDocs(response.data.grouped);
      
      // Auto-expand first category
      if (Object.keys(response.data.grouped).length > 0) {
        const firstCategory = Object.keys(response.data.grouped)[0];
        setExpandedCategories({ [firstCategory]: true });
      }
    } catch (error) {
      toast.error('Failed to fetch documents');
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!SUPPORTED_FORMATS.includes(file.type)) {
      toast.error('Unsupported file format. Please upload DOCX, PDF, PNG, JPEG, or JPG files.');
      return;
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      toast.error('File size must be less than 10MB');
      return;
    }

    setUploadForm({ ...uploadForm, file });
  };

  const handleUpload = async () => {
    if (!uploadForm.category || !uploadForm.doc_type || !uploadForm.file) {
      toast.error('Please fill in all fields and select a file');
      return;
    }

    setUploading(true);

    try {
      // Convert file to base64
      const reader = new FileReader();
      reader.onload = async () => {
        const base64Content = reader.result.split(',')[1];

        const uploadData = {
          filename: uploadForm.file.name,
          category: uploadForm.category,
          doc_type: uploadForm.doc_type,
          file_content: base64Content,
          mime_type: uploadForm.file.type,
          file_size: uploadForm.file.size
        };

        await axios.post(`${API}/document-files/upload`, uploadData);
        toast.success('Document uploaded successfully!');
        setUploadDialogOpen(false);
        setUploadForm({ category: '', doc_type: '', file: null });
        fetchDocuments();
      };
      reader.readAsDataURL(uploadForm.file);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleDocumentClick = async (doc) => {
    try {
      // Clear previous render
      setDocxRenderKey(prev => prev + 1);
      setSelectedDoc(null); // Clear current doc first
      setPdfError(false); // Reset PDF error state
      setUseEmbedForPdf(false); // Reset embed fallback
      
      // Revoke previous PDF blob URL if exists
      if (pdfBlobUrl) {
        URL.revokeObjectURL(pdfBlobUrl);
        setPdfBlobUrl(null);
      }
      
      const response = await axios.get(`${API}/document-files/${doc.id}`);
      /*console.log('Document loaded:', {
        id: response.data.id,
        filename: response.data.filename,
        mime_type: response.data.mime_type,
        file_size: response.data.file_size,
        has_content: !!response.data.file_content,
        content_length: response.data.file_content?.length || 0
      }); */
      
      // For PDFs, create a Blob URL instead of using data URI
      if (response.data.mime_type?.includes('pdf') && response.data.file_content) {
        try {
          const byteCharacters = atob(response.data.file_content);
          const byteArray = new Uint8Array(byteCharacters.length);
          for (let i = 0; i < byteCharacters.length; i++) {
            byteArray[i] = byteCharacters.charCodeAt(i);
          }
          const blob = new Blob([byteArray], { type: 'application/pdf' });
          const blobUrl = URL.createObjectURL(blob);
          setPdfBlobUrl(blobUrl);
          console.log('Created PDF Blob URL:', blobUrl);
        } catch (blobError) {
          console.error('Error creating PDF Blob URL:', blobError);
          toast.error('Error processing PDF file');
        }
      }
      
      setSelectedDoc(response.data);
    } catch (error) {
      console.error('Failed to load document:', error);
      toast.error('Failed to load document');
    }
  };

 const renderDocxPreview = async (base64Content) => {
  try {
    setRenderingDocx(true);
    setDocxHtml(''); // Clear previous content

    // Convert base64 to ArrayBuffer
    const byteCharacters = atob(base64Content);
    const byteArray = new Uint8Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteArray[i] = byteCharacters.charCodeAt(i);
    }
    const arrayBuffer = byteArray.buffer;

    // Create a temporary container element
    const tempContainer = document.createElement('div');
    
    // Render to temporary container
    await renderAsync(arrayBuffer, tempContainer, null, {
      className: "docx-wrapper",
      inWrapper: true,
      ignoreWidth: false,
      ignoreHeight: false,
      renderHeaders: true,
      renderFooters: true,
      useBase64URL: false,
    });

    // Get the HTML and set it to state
    setDocxHtml(tempContainer.innerHTML);
    setRenderingDocx(false);
  } catch (error) {
    console.error("Error rendering DOCX:", error);
    toast.error("Failed to load content");
    setRenderingDocx(false);
  }
};


  const handleDownload = () => {
    if (!selectedDoc) return;

    const link = document.createElement('a');
    link.href = `data:${selectedDoc.mime_type};base64,${selectedDoc.file_content}`;
    link.download = selectedDoc.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success('Download started');
  };

  const handleDelete = async (docId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;

    try {
      await axios.delete(`${API}/document-files/${docId}`);
      toast.success('Document deleted successfully');
      setSelectedDoc(null);
      fetchDocuments();
    } catch (error) {
      toast.error('Failed to delete document');
    }
  };

  const handleScrapeZuciCaseStudies = async () => {
    if (!window.confirm('This will scrape case studies from Zuci Systems website and add them to your documents. This may take a few minutes. Continue?')) return;

    setScrapingZuci(true);
    toast.loading('Scraping Zuci case studies...', { id: 'scraping' });

    try {
      const response = await axios.post(`${API}/document-files/scrape-zuci-case-studies`);
      
      if (response.data.success) {
        toast.success(
          `Successfully scraped ${response.data.total_saved} case studies!`,
          { id: 'scraping' }
        );
        fetchDocuments();
      } else {
        toast.error(response.data.message || 'Failed to scrape case studies', { id: 'scraping' });
      }
    } catch (error) {
      toast.error(
        error.response?.data?.detail || 'Failed to scrape case studies',
        { id: 'scraping' }
      );
    } finally {
      setScrapingZuci(false);
    }
  };

  const toggleCategory = (category) => {
    setExpandedCategories({
      ...expandedCategories,
      [category]: !expandedCategories[category]
    });
  };

  const toggleType = (category, type) => {
    const key = `${category}-${type}`;
    setExpandedTypes({
      ...expandedTypes,
      [key]: !expandedTypes[key]
    });
  };

  const getFileIcon = (mimeType) => {
    if (mimeType?.includes('image')) return <FileImage className="w-5 h-5 text-purple-600" />;
    if (mimeType?.includes('pdf')) return <FileText className="w-5 h-5 text-red-600" />;
    return <File className="w-5 h-5 text-blue-600" />;
  };

  const filteredDocs = documents.filter(doc =>
    doc.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
    doc.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
    doc.doc_type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const renderDocumentPreview = () => {
    if (!selectedDoc) {
      return (
        <div className="flex items-center justify-center h-full text-gray-500">
          <div className="text-center">
            <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p>Select a document to preview</p>
          </div>
        </div>
      );
    }

    const isImage = selectedDoc.mime_type?.includes('image');
    const isPdf = selectedDoc.mime_type?.includes('pdf');
    const isDocx = selectedDoc.mime_type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';



    return (
      <div className="h-full flex flex-col">
        {/* Document Header */}
        <div className="border-b border-gray-200 p-4 bg-white">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                {getFileIcon(selectedDoc.mime_type)}
                <h2 className="text-xl font-bold text-gray-900">{selectedDoc.filename}</h2>
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span className="px-2 py-1 bg-indigo-100 text-indigo-700 rounded-full text-xs font-medium">
                  {selectedDoc.category}
                </span>
                <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                  {selectedDoc.doc_type}
                </span>
                <span>{(selectedDoc.file_size / 1024).toFixed(2)} KB</span>
              </div>
            </div>
            <div className="flex gap-2">
              <Button onClick={handleDownload} variant="outline" size="sm">
                <Download size={16} className="mr-2" />
                Download
              </Button>
              <Button
                onClick={() => handleDelete(selectedDoc.id)}
                variant="destructive"
                size="sm"
              >
                <Trash2 size={16} className="mr-2" />
                Delete
              </Button>
            </div>
          </div>
        </div>

        {/* Document Preview */}
        <div className="flex-1 overflow-auto bg-gray-50 p-6">
          {isImage && (
            <div className="flex items-center justify-center h-full">
              <img
                src={`data:${selectedDoc.mime_type};base64,${selectedDoc.file_content}`}
                alt={selectedDoc.filename}
                className="max-w-full max-h-full object-contain rounded-lg shadow-lg"
              />
            </div>
          )}
          {isPdf && (
            <div className="h-full">
              {pdfBlobUrl && !pdfError ? (
                <div className="relative h-full">
                  <iframe
                    key={`iframe-${selectedDoc.id}`}
                    src={pdfBlobUrl}
                    className="w-full h-full rounded-lg shadow-lg"
                    title={selectedDoc.filename}
                    onError={() => {
                      console.error('PDF iframe rendering failed');
                      setPdfError(true);
                    }}
                  />
                </div>
              ) : pdfError ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <FileText className="w-16 h-16 mx-auto mb-4 text-red-400" />
                    <p className="text-gray-900 font-semibold mb-2">Unable to Preview PDF</p>
                    <p className="text-gray-600 mb-4">The PDF couldn't be displayed in the browser.</p>
                    <div className="flex gap-2 justify-center">
                      <Button onClick={handleDownload} className="bg-indigo-600 hover:bg-indigo-700">
                        <Download size={16} className="mr-2" />
                        Download to View
                      </Button>
                      <Button 
                        onClick={() => {
                          setPdfError(false);
                          handleDocumentClick(selectedDoc);
                        }} 
                        variant="outline"
                      >
                        Try Again
                      </Button>
                    </div>
                  </div>
                </div>
              ) : !pdfBlobUrl && selectedDoc.file_content ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <Loader className="w-12 h-12 mx-auto mb-4 animate-spin text-indigo-600" />
                    <p className="text-gray-600">Processing PDF...</p>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <FileText className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                    <p className="text-gray-600 mb-4">PDF content not available</p>
                    <Button onClick={handleDownload}>
                      <Download size={16} className="mr-2" />
                      Download PDF
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
          {isDocx && (
            <div key={docxRenderKey} className="h-full bg-white rounded-lg shadow-lg overflow-auto">
              {renderingDocx ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <Loader className="w-12 h-12 mx-auto mb-4 animate-spin text-indigo-600" />
                    <p className="text-gray-600">Rendering document...</p>
                  </div>
                </div>
              ) : (
                <div
                  className="p-8"
                  style={{
                    minHeight: '100%',
                    backgroundColor: 'white'
                  }}
                  dangerouslySetInnerHTML={{ __html: docxHtml }}
                />
              )}
            </div>
          )}
          {!isImage && !isPdf && !isDocx && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <FileText className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                <p className="text-gray-600 mb-4">Preview not available for this file type</p>
                <Button onClick={handleDownload}>
                  <Download size={16} className="mr-2" />
                  Download to View
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  console.log('groupedDocs', groupedDocs)

  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="h-[calc(100vh-4rem)]">
        {/* Header */}
        <div className="px-8 pt-6 pb-4 border-b border-gray-200 bg-white">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-1">Document Management</h1>
              <p className="text-gray-600">Upload and organize your documents by category and type</p>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={handleScrapeZuciCaseStudies}
                disabled={scrapingZuci}
                variant="outline"
                className="border-indigo-600 text-indigo-600 hover:bg-indigo-50"
              >
                {scrapingZuci ? (
                  <>
                    <Loader size={16} className="mr-2 animate-spin" />
                    Scraping...
                  </>
                ) : (
                  <>
                    <Globe size={16} className="mr-2" />
                    Get Zuci Case Studies
                  </>
                )}
              </Button>
              <Button
                onClick={() => setUploadDialogOpen(true)}
                className="bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700"
              >
                <Plus size={16} className="mr-2" />
                Upload Document
              </Button>
            </div>
          </div>
        </div>

        <ResizablePanelGroup direction="horizontal" className="h-[calc(100%-100px)]">
          {/* LEFT PANEL - Document List */}
          <ResizablePanel defaultSize={35} minSize={25}>
            <div className="h-full overflow-y-auto bg-gray-50 p-4">
              {/* Search */}
              <div className="mb-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                  <Input
                    placeholder="Search documents..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              {/* Document Tree */}
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader className="w-8 h-8 animate-spin text-indigo-600" />
                </div>
              ) : Object.keys(groupedDocs).length === 0 ? (
                <div className="text-center py-12">
                  <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                  <p className="text-gray-500 mb-4">No documents uploaded yet</p>
                  <Button onClick={() => setUploadDialogOpen(true)} size="sm">
                    <Plus size={16} className="mr-2" />
                    Upload First Document
                  </Button>
                </div>
              ) : (
                <div className="space-y-2">
                  {Object.entries(groupedDocs).map(([category, types]) => (
                    <div key={category} className="bg-white rounded-lg border border-gray-200">
                      <button
                        onClick={() => toggleCategory(category)}
                        className="w-full flex items-center justify-between p-3 hover:bg-gray-50 transition-colors"
                      >
                        <div className="flex items-center gap-2">
                          {expandedCategories[category] ? (
                            <ChevronDown size={18} className="text-gray-600" />
                          ) : (
                            <ChevronRight size={18} className="text-gray-600" />
                          )}
                          <span className="font-semibold text-gray-900">{category}</span>
                          <span className="text-xs text-gray-500">
                            ({Object.values(types).flat().length})
                          </span>
                        </div>
                      </button>

                      {expandedCategories[category] && (
                        <div className="px-3 pb-3 space-y-2">
                          {Object.entries(types).map(([type, docs]) => (
                            <div key={`${category}-${type}`} className="ml-4">
                              <button
                                onClick={() => toggleType(category, type)}
                                className="w-full flex items-center justify-between p-2 hover:bg-gray-50 rounded transition-colors"
                              >
                                <div className="flex items-center gap-2">
                                  {expandedTypes[`${category}-${type}`] ? (
                                    <ChevronDown size={16} className="text-gray-500" />
                                  ) : (
                                    <ChevronRight size={16} className="text-gray-500" />
                                  )}
                                  <span className="font-medium text-gray-700 text-sm">{type}</span>
                                  <span className="text-xs text-gray-400">({docs.length})</span>
                                </div>
                              </button>

                              {expandedTypes[`${category}-${type}`] && (
                                <div className="ml-6 mt-1 space-y-1">
                                  {docs.map((doc) => (
                                    <button
                                      key={doc.id}
                                      onClick={() => handleDocumentClick(doc)}
                                      className={`w-full flex items-center gap-2 p-2 rounded text-sm hover:bg-indigo-50 transition-colors text-left ${
                                        selectedDoc?.id === doc.id ? 'bg-indigo-100 border border-indigo-300' : ''
                                      }`}
                                    >
                                      {getFileIcon(doc.mime_type)}
                                      <span className="flex-1 truncate">{doc.filename}</span>
                                    </button>
                                  ))}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </ResizablePanel>

          <ResizableHandle withHandle />

          {/* RIGHT PANEL - Document Preview */}
          <ResizablePanel defaultSize={65} minSize={40}>
            <div className="h-full bg-white">
              {renderDocumentPreview()}
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>

      {/* Upload Dialog */}
      <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Upload Document</DialogTitle>
          </DialogHeader>

          <div className="space-y-4 mt-4">
            <div>
              <Label>Category *</Label>
              <Select
                value={uploadForm.category}
                onValueChange={(value) => setUploadForm({ ...uploadForm, category: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  {CATEGORIES.map(cat => (
                    <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Document Type *</Label>
              <Select
                value={uploadForm.doc_type}
                onValueChange={(value) => setUploadForm({ ...uploadForm, doc_type: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  {DOC_TYPES.map(type => (
                    <SelectItem key={type} value={type}>{type}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>File *</Label>
              <div className="mt-1">
                <input
                  type="file"
                  accept=".pdf,.docx,.png,.jpg,.jpeg"
                  onChange={handleFileSelect}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                />
              </div>
              {uploadForm.file && (
                <p className="text-sm text-gray-600 mt-2">
                  Selected: {uploadForm.file.name} ({(uploadForm.file.size / 1024).toFixed(2)} KB)
                </p>
              )}
              <p className="text-xs text-gray-500 mt-1">
                Supported formats: PDF, DOCX, PNG, JPEG, JPG (Max 10MB)
              </p>
            </div>

            <div className="flex justify-end gap-2 pt-4">
              <Button
                variant="outline"
                onClick={() => {
                  setUploadDialogOpen(false);
                  setUploadForm({ category: '', doc_type: '', file: null });
                }}
                disabled={uploading}
              >
                Cancel
              </Button>
              <Button
                onClick={handleUpload}
                disabled={uploading || !uploadForm.category || !uploadForm.doc_type || !uploadForm.file}
                className="bg-indigo-600 hover:bg-indigo-700"
              >
                {uploading ? (
                  <>
                    <Loader size={16} className="mr-2 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload size={16} className="mr-2" />
                    Upload
                  </>
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </Layout>
  );
};

export default DocumentManagement;
