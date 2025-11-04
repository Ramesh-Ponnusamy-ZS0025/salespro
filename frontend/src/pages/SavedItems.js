import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { toast } from 'sonner';
import { Bookmark, Megaphone, FileText, Globe, Filter } from 'lucide-react';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Input } from '../components/ui/input';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SavedItems = ({ user, onLogout }) => {
  const [campaigns, setCampaigns] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [gtmAssets, setGtmAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [campaignsRes, documentsRes, gtmRes] = await Promise.all([
        axios.get(`${API}/campaigns`),
        axios.get(`${API}/documents`),
        axios.get(`${API}/gtm`),
      ]);
      setCampaigns(campaignsRes.data);
      setDocuments(documentsRes.data);
      setGtmAssets(gtmRes.data);
    } catch (error) {
      toast.error('Failed to fetch saved items');
    } finally {
      setLoading(false);
    }
  };

  const filterItems = (items, searchFields) => {
    if (!searchQuery.trim()) return items;
    const query = searchQuery.toLowerCase();
    return items.filter(item =>
      searchFields.some(field => 
        item[field]?.toString().toLowerCase().includes(query)
      )
    );
  };

  const filteredCampaigns = filterItems(campaigns, ['campaign_name', 'service', 'stage']);
  const filteredDocuments = filterItems(documents, ['template_type', 'engagement_model']);
  const filteredGtmAssets = filterItems(gtmAssets, ['company_name', 'offering']);

  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="p-8" data-testid="saved-items-page">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-slate-900 mb-2">Saved Items & Configuration</h1>
            <p className="text-slate-600">Central hub for all your campaigns, documents, and assets</p>
          </div>

          {/* Search Bar */}
          <div className="mb-6">
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={20} />
              <Input
                data-testid="search-input"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search across all saved items..."
                className="pl-10 bg-white border-slate-200"
              />
            </div>
          </div>

          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
          ) : (
            <Tabs defaultValue="campaigns" className="w-full">
              <TabsList className="grid grid-cols-3 mb-6">
                <TabsTrigger value="campaigns" data-testid="campaigns-tab">
                  <Megaphone size={16} className="mr-2" />
                  Campaigns ({filteredCampaigns.length})
                </TabsTrigger>
                <TabsTrigger value="documents" data-testid="documents-tab">
                  <FileText size={16} className="mr-2" />
                  Documents ({filteredDocuments.length})
                </TabsTrigger>
                <TabsTrigger value="gtm" data-testid="gtm-tab">
                  <Globe size={16} className="mr-2" />
                  GTM Assets ({filteredGtmAssets.length})
                </TabsTrigger>
              </TabsList>

              {/* Campaigns Tab */}
              <TabsContent value="campaigns">
                {filteredCampaigns.length > 0 ? (
                  <div className="space-y-4">
                    {filteredCampaigns.map((campaign) => (
                      <Card
                        key={campaign.id}
                        data-testid={`saved-campaign-${campaign.id}`}
                        className="p-6 bg-white border border-slate-200 shadow hover:shadow-lg transition-shadow"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <h3 className="text-lg font-bold text-slate-900 mb-2">{campaign.campaign_name}</h3>
                            <div className="flex items-center gap-2 flex-wrap">
                              <Badge className="bg-indigo-100 text-indigo-700">{campaign.service}</Badge>
                              <Badge className="bg-blue-100 text-blue-700">{campaign.stage}</Badge>
                              <Badge
                                className={`${
                                  campaign.status === 'published'
                                    ? 'bg-green-100 text-green-700'
                                    : campaign.status === 'review'
                                    ? 'bg-yellow-100 text-yellow-700'
                                    : 'bg-slate-100 text-slate-700'
                                }`}
                              >
                                {campaign.status}
                              </Badge>
                            </div>
                          </div>
                          <Bookmark className="text-indigo-600" size={20} />
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <p className="text-slate-600 font-medium">Target ICP:</p>
                            <p className="text-slate-800">{campaign.icp.join(', ')}</p>
                          </div>
                          <div>
                            <p className="text-slate-600 font-medium">Tone:</p>
                            <p className="text-slate-800">{campaign.tone}</p>
                          </div>
                        </div>
                        {campaign.ai_content && (
                          <div className="mt-4 p-3 bg-slate-50 rounded-lg border border-slate-200">
                            <p className="text-xs font-semibold text-slate-700 mb-1">Generated Copy:</p>
                            <p className="text-sm text-slate-700 line-clamp-2">{campaign.ai_content}</p>
                          </div>
                        )}
                      </Card>
                    ))}
                  </div>
                ) : (
                  <Card className="p-12 bg-white border border-slate-200 text-center">
                    <Megaphone className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-slate-900 mb-2">
                      {searchQuery ? 'No matching campaigns' : 'No campaigns saved'}
                    </h3>
                    <p className="text-slate-600">
                      {searchQuery
                        ? 'Try adjusting your search query'
                        : 'Create your first campaign to see it here'}
                    </p>
                  </Card>
                )}
              </TabsContent>

              {/* Documents Tab */}
              <TabsContent value="documents">
                {filteredDocuments.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filteredDocuments.map((doc) => (
                      <Card
                        key={doc.id}
                        data-testid={`saved-document-${doc.id}`}
                        className="p-6 bg-white border border-slate-200 shadow hover:shadow-lg transition-shadow"
                      >
                        <div className="flex items-start justify-between mb-4">
                          <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center">
                            <FileText className="text-indigo-600" size={24} />
                          </div>
                          <Bookmark className="text-indigo-600" size={18} />
                        </div>
                        <h3 className="text-lg font-bold text-slate-900 mb-2">
                          {doc.template_type.toUpperCase()}
                        </h3>
                        <div className="space-y-2">
                          <div>
                            <p className="text-xs text-slate-600">Engagement Model:</p>
                            <Badge variant="outline">{doc.engagement_model}</Badge>
                          </div>
                          <div>
                            <p className="text-xs text-slate-600">Status:</p>
                            <Badge className="bg-green-100 text-green-700">{doc.status}</Badge>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <Card className="p-12 bg-white border border-slate-200 text-center">
                    <FileText className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-slate-900 mb-2">
                      {searchQuery ? 'No matching documents' : 'No documents generated'}
                    </h3>
                    <p className="text-slate-600">
                      {searchQuery
                        ? 'Try adjusting your search query'
                        : 'Generate your first document to see it here'}
                    </p>
                  </Card>
                )}
              </TabsContent>

              {/* GTM Assets Tab */}
              <TabsContent value="gtm">
                {filteredGtmAssets.length > 0 ? (
                  <div className="space-y-4">
                    {filteredGtmAssets.map((asset) => (
                      <Card
                        key={asset.id}
                        data-testid={`saved-gtm-${asset.id}`}
                        className="p-6 bg-white border border-slate-200 shadow hover:shadow-lg transition-shadow"
                      >
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1">
                            <h3 className="text-lg font-bold text-slate-900 mb-2">{asset.company_name}</h3>
                            <Badge className="bg-purple-100 text-purple-700">{asset.status}</Badge>
                          </div>
                          <Globe className="text-indigo-600" size={24} />
                        </div>
                        <div className="space-y-2">
                          <div>
                            <p className="text-xs font-semibold text-slate-700">Offering:</p>
                            <p className="text-sm text-slate-800 line-clamp-2">{asset.offering}</p>
                          </div>
                          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                            <p className="text-xs font-semibold text-slate-700 mb-1">Generated Prompt:</p>
                            <p className="text-xs text-slate-700 line-clamp-3">{asset.prompt}</p>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <Card className="p-12 bg-white border border-slate-200 text-center">
                    <Globe className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-slate-900 mb-2">
                      {searchQuery ? 'No matching GTM assets' : 'No GTM assets generated'}
                    </h3>
                    <p className="text-slate-600">
                      {searchQuery
                        ? 'Try adjusting your search query'
                        : 'Generate your first GTM prompt to see it here'}
                    </p>
                  </Card>
                )}
              </TabsContent>
            </Tabs>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default SavedItems;
