import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import { toast } from 'sonner';
import { Plus, ArrowRight, Megaphone } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import CampaignEditor from '../components/CampaignEditor';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CampaignBuilder = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [campaigns, setCampaigns] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentStep, setCurrentStep] = useState('list');
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [editMode, setEditMode] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [campaignsRes, agentsRes] = await Promise.all([
        axios.get(`${API}/campaigns`),
        axios.get(`${API}/agents`),
      ]);
      setCampaigns(campaignsRes.data);
      setAgents(agentsRes.data);
    } catch (error) {
      toast.error('Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCampaign = () => {
    setSelectedCampaign(null);
    setEditMode(false);
    setCurrentStep('editor');
  };

  const handleEditCampaign = (campaign) => {
    setSelectedCampaign(campaign);
    setEditMode(true);
    setCurrentStep('editor');
  };

  const handleBackToList = () => {
    setCurrentStep('list');
    setSelectedCampaign(null);
    setEditMode(false);
    fetchData();
  };

  if (currentStep === 'list') {
    return (
      <Layout user={user} onLogout={onLogout}>
        <div className="p-8" data-testid="campaign-builder-page">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-4xl font-bold text-slate-900 mb-2">Campaign Builder</h1>
              <p className="text-slate-600">Design multi-touch outbound campaigns with AI</p>
            </div>
            <Button
              onClick={handleCreateCampaign}
              data-testid="create-campaign-button"
              className="bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 text-white shadow-lg"
            >
              <Plus size={20} className="mr-2" />
              Create Campaign
            </Button>
          </div>

          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
          ) : campaigns.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-xl border border-slate-200">
              <Megaphone className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-slate-900 mb-2">No campaigns yet</h3>
              <p className="text-slate-600">Create your first campaign to start engaging prospects</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {campaigns.map((campaign) => (
                <Card
                  key={campaign.id}
                  className="p-6 bg-white border border-slate-200 shadow-lg hover:shadow-xl transition-shadow"
                >
                  <h3 className="text-lg font-bold text-slate-900 mb-2">{campaign.campaign_name}</h3>
                  <div className="flex items-center gap-2 mb-3">
                    <span className="px-2 py-1 bg-indigo-100 text-indigo-700 text-xs rounded-full">{campaign.service}</span>
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">{campaign.stage}</span>
                  </div>
                  <p className="text-sm text-slate-600 mb-4">ICP: {campaign.icp?.join(', ')}</p>
                  <Button 
                    variant="outline" 
                    className="w-full"
                    onClick={() => handleEditCampaign(campaign)}
                  >
                    Edit Campaign <ArrowRight size={16} className="ml-2" />
                  </Button>
                </Card>
              ))}
            </div>
          )}
        </div>
      </Layout>
    );
  }

  if (currentStep === 'editor') {
    return (
      <CampaignEditor
        campaign={selectedCampaign}
        agents={agents}
        user={user}
        onLogout={onLogout}
        onBack={handleBackToList}
        editMode={editMode}
      />
    );
  }

  return null;
};

export default CampaignBuilder;
