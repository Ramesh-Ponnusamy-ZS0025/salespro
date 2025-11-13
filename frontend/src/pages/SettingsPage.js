import React, { useState, useEffect } from 'react';
import { Settings, Cloud, Link, Check, X, Loader, ExternalLink, AlertCircle } from 'lucide-react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

const SettingsPage = () => {
  const [cloudConfig, setCloudConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);
  const [drives, setDrives] = useState([]);
  const [authWindow, setAuthWindow] = useState(null);
  const [oauthConfigured, setOauthConfigured] = useState(false);
  const [setupInstructions, setSetupInstructions] = useState(null);
  const [checkingConfig, setCheckingConfig] = useState(true);

  useEffect(() => {
    checkOAuthConfiguration();
    fetchCloudConfig();
    
    // Listen for OAuth success message
    const handleMessage = (event) => {
      console.log('Message received in parent window:', event);
      console.log('Event origin:', event.origin);
      console.log('Event data:', event.data);
      console.log('Window origin:', window.location.origin);
      
      // Accept messages from localhost:8001 (backend) or localhost:3000 (frontend)
      const allowedOrigins = [
        'http://localhost:3000',
        'http://localhost:8001',
        window.location.origin
      ];
      
      if (!allowedOrigins.includes(event.origin)) {
        console.warn('Message from unauthorized origin:', event.origin);
        return;
      }
      
      if (event.data && event.data.type === 'oauth_success') {
        console.log('OAuth success message received!', event.data);
        setConnecting(false);
        fetchCloudConfig();
      }
    };
    
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  const checkOAuthConfiguration = async () => {
    try {
      setCheckingConfig(true);
      const response = await axios.get(`${API_BASE}/cloud-storage/oauth/status`);
      setOauthConfigured(response.data.configured);
      
      if (!response.data.configured) {
        setSetupInstructions(response.data.setup_instructions);
      }
    } catch (error) {
      console.error('Failed to check OAuth config:', error);
      setOauthConfigured(false);
    } finally {
      setCheckingConfig(false);
    }
  };

  const fetchCloudConfig = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('auth_token');
      const response = await axios.get(`${API_BASE}/cloud-storage/config`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.configured) {
        setCloudConfig(response.data.config);
        // Fetch available drives if configured
        fetchDrives();
      }
    } catch (error) {
      console.error('Failed to fetch cloud config:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDrives = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await axios.get(`${API_BASE}/cloud-storage/drives`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDrives(response.data.drives || []);
    } catch (error) {
      console.error('Failed to fetch drives:', error);
    }
  };

  const handleConnectCloud = async () => {
    if (!oauthConfigured) {
      alert('Azure OAuth is not configured. Please follow the setup instructions below.');
      return;
    }

    try {
      setConnecting(true);
      const token = localStorage.getItem('auth_token');
      
      // Get authorization URL from backend
      const response = await axios.get(`${API_BASE}/cloud-storage/oauth/authorize`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const { authorization_url } = response.data;
      
      // Open OAuth popup
      const width = 600;
      const height = 700;
      const left = window.screenX + (window.outerWidth - width) / 2;
      const top = window.screenY + (window.outerHeight - height) / 2;
      
      const popup = window.open(
        authorization_url,
        'Microsoft OAuth',
        `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`
      );
      
      setAuthWindow(popup);
      
      // Check if popup was blocked
      if (!popup || popup.closed) {
        alert('Pop-up blocked. Please allow pop-ups for this site and try again.');
        setConnecting(false);
        return;
      }
      
      // Monitor popup
      const checkPopup = setInterval(() => {
        if (popup.closed) {
          clearInterval(checkPopup);
          setConnecting(false);
          setAuthWindow(null);
        }
      }, 500);
      
    } catch (error) {
      console.error('Failed to start OAuth:', error);
      const errorMsg = error.response?.data?.detail || 'Failed to start authentication';
      alert(errorMsg);
      setConnecting(false);
    }
  };

  const handleDisconnect = async () => {
    if (!window.confirm('Are you sure you want to disconnect cloud storage?')) {
      return;
    }

    try {
      const token = localStorage.getItem('auth_token');
      await axios.delete(`${API_BASE}/cloud-storage/config/${cloudConfig.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      alert('Cloud storage disconnected');
      setCloudConfig(null);
      setDrives([]);
    } catch (error) {
      alert('Failed to disconnect');
    }
  };

  const handleUpdateDrive = async (driveId) => {
    try {
      const token = localStorage.getItem('auth_token');
      const selectedDrive = drives.find(d => d.id === driveId);
      
      await axios.put(
        `${API_BASE}/cloud-storage/config/${cloudConfig.id}`,
        { 
          drive_id: driveId,
          drive_name: selectedDrive?.name 
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      fetchCloudConfig();
      alert('Drive updated successfully');
    } catch (error) {
      alert('Failed to update drive');
    }
  };

  if (loading || checkingConfig) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-md">
          {/* Header */}
          <div className="border-b px-6 py-4">
            <div className="flex items-center gap-3">
              <Settings className="w-6 h-6 text-gray-700" />
              <h1 className="text-2xl font-bold text-gray-800">Settings</h1>
            </div>
          </div>

          {/* Cloud Storage Section */}
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-semibold text-gray-800 flex items-center gap-2">
                  <Cloud className="w-5 h-5" />
                  Cloud Storage Integration
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  Connect OneDrive or SharePoint to access case study files
                </p>
              </div>
              
              {cloudConfig && (
                <div className="flex items-center gap-2 px-3 py-1.5 bg-green-50 border border-green-200 rounded-lg">
                  <Check className="w-5 h-5 text-green-600" />
                  <span className="font-medium text-green-700">Connected</span>
                </div>
              )}
            </div>

            {/* Configuration Warning */}
            {!oauthConfigured && (
              <div className="mb-6 bg-orange-50 border-l-4 border-orange-500 p-4 rounded">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-6 h-6 text-orange-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-semibold text-orange-900 mb-2">Azure OAuth Not Configured</h3>
                    <p className="text-sm text-orange-800 mb-3">
                      The backend needs Azure OAuth credentials to enable cloud storage connection. 
                      Please follow these steps:
                    </p>
                    
                    {setupInstructions && (
                      <div className="bg-white rounded p-3 text-xs text-gray-700 space-y-1">
                        {Object.entries(setupInstructions).map(([key, value]) => (
                          <div key={key}>
                            <strong>{key.replace('step', 'Step ')}:</strong> {value}
                          </div>
                        ))}
                      </div>
                    )}
                    
                    <a
                      href="https://portal.azure.com"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 mt-3 px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700 text-sm"
                    >
                      <ExternalLink className="w-4 h-4" />
                      Open Azure Portal
                    </a>
                  </div>
                </div>
              </div>
            )}

            {!cloudConfig && oauthConfigured && (
              <div className="space-y-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-semibold text-blue-900 mb-2">What you'll get:</h3>
                  <ul className="space-y-2 text-sm text-blue-800">
                    <li className="flex items-start gap-2">
                      <Check className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      <span>Access your OneDrive and SharePoint files directly in TaRaZ</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      <span>Automatically fetch case study files by category</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      <span>Use files in Thread Intelligence for better context</span>
                    </li>
                  </ul>
                </div>

                <button
                  onClick={handleConnectCloud}
                  disabled={connecting}
                  className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg"
                >
                  {connecting ? (
                    <>
                      <Loader className="w-5 h-5 animate-spin" />
                      Connecting...
                    </>
                  ) : (
                    <>
                      <ExternalLink className="w-5 h-5" />
                      Connect with Microsoft
                    </>
                  )}
                </button>

                {connecting && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <p className="text-sm text-yellow-800">
                      <strong>Note:</strong> A popup window will open for authentication. 
                      If you don't see it, check if your browser blocked pop-ups.
                    </p>
                  </div>
                )}
              </div>
            )}

            {cloudConfig && (
              <div className="space-y-4">
                {/* Connection Info */}
                <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Storage Type:</span>
                      <span className="font-medium text-gray-800 capitalize">
                        {cloudConfig.storage_type}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Folder Path:</span>
                      <span className="font-medium text-gray-800">{cloudConfig.folder_path}</span>
                    </div>
                    {cloudConfig.drive_name && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Drive:</span>
                        <span className="font-medium text-gray-800">{cloudConfig.drive_name}</span>
                      </div>
                    )}
                    {cloudConfig.token_expires_at && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Token Expires:</span>
                        <span className="font-medium text-gray-800">
                          {new Date(cloudConfig.token_expires_at).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Drive Selection */}
                {drives.length > 0 && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Select Drive
                    </label>
                    <select
                      value={cloudConfig.drive_id || ''}
                      onChange={(e) => handleUpdateDrive(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">Choose a drive...</option>
                      {drives.map((drive) => (
                        <option key={drive.id} value={drive.id}>
                          {drive.name} ({drive.driveType})
                        </option>
                      ))}
                    </select>
                    <p className="text-xs text-gray-500 mt-1">
                      Select which drive to use for case study files
                    </p>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-3 pt-4">
                  <button
                    onClick={handleDisconnect}
                    className="flex items-center gap-2 px-4 py-2 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 transition-colors border border-red-200"
                  >
                    <X className="w-4 h-4" />
                    Disconnect
                  </button>
                  
                  <button
                    onClick={handleConnectCloud}
                    className="flex items-center gap-2 px-4 py-2 bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors border border-gray-200"
                  >
                    <Link className="w-4 h-4" />
                    Reconnect
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Setup Instructions */}
        {oauthConfigured && (
          <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-3">How it works:</h3>
            <ol className="list-decimal list-inside space-y-2 text-sm text-blue-800">
              <li>Click "Connect with Microsoft" button above</li>
              <li>Sign in with your Microsoft account in the popup window</li>
              <li>Grant permissions to access your files</li>
              <li>Connection will be established automatically</li>
              <li>Select a drive if you have multiple OneDrive/SharePoint locations</li>
              <li>Your case study files will be available in Thread Intelligence</li>
            </ol>
            
            <div className="mt-4 pt-4 border-t border-blue-200">
              <p className="text-xs text-blue-700">
                <strong>Privacy:</strong> We only request read-only access to your files. 
                Your access tokens are securely stored and never shared.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SettingsPage;
