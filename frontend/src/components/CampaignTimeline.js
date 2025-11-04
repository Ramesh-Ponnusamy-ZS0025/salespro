import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import Layout from './Layout';
import { toast } from 'sonner';
import { ArrowLeft, Mail, MessageSquare, Phone, Sparkles, Copy, FileDown, Send, Edit2 } from 'lucide-react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Card } from './ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CampaignTimeline = ({ campaign, user, onLogout, onBack }) => {
  const [sequence, setSequence] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generatingStep, setGeneratingStep] = useState(null);
  const [editingStep, setEditingStep] = useState(null);
  const [editContent, setEditContent] = useState('');

  useEffect(() => {
    fetchSequence();
  }, [campaign.id]);

  const fetchSequence = async () => {
    try {
      const response = await axios.get(`${API}/campaigns/${campaign.id}/sequence`);
      setSequence(response.data);
    } catch (error) {
      toast.error('Failed to fetch sequence');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateContent = async (stepNumber) => {
    setGeneratingStep(stepNumber);
    try {
      const response = await axios.post(
        `${API}/campaigns/${campaign.id}/sequence/steps/${stepNumber}/generate`
      );
      toast.success('Content generated!');
      await fetchSequence();
    } catch (error) {
      toast.error('Failed to generate content');
    } finally {
      setGeneratingStep(null);
    }
  };

  const handleEditContent = (step) => {
    setEditingStep(step);
    setEditContent(step.content || '');
  };

  const handleSaveEdit = async () => {
    try {
      await axios.put(
        `${API}/campaigns/${campaign.id}/sequence/steps/${editingStep.step_number}`,
        { content: editContent }
      );
      toast.success('Content updated!');
      setEditingStep(null);
      await fetchSequence();
    } catch (error) {
      toast.error('Failed to update content');
    }
  };

  const handleDragEnd = async (result) => {
    if (!result.destination) return;

    const items = Array.from(sequence.steps);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    // Update local state immediately for smooth UX
    setSequence({ ...sequence, steps: items });

    // Send new order to backend
    const newOrder = items.map(item => item.step_number);
    try {
      await axios.put(`${API}/campaigns/${campaign.id}/sequence/reorder`, newOrder);
      toast.success('Sequence reordered!');
      await fetchSequence();
    } catch (error) {
      toast.error('Failed to reorder sequence');
      await fetchSequence(); // Revert on error
    }
  };

  const getChannelIcon = (channel) => {
    switch (channel) {
      case 'email':
        return <Mail className="text-white" size={20} />;
      case 'linkedin':
        return <MessageSquare className="text-white" size={20} />;
      case 'voicemail':
        return <Phone className="text-white" size={20} />;
      default:
        return <Mail className="text-white" size={20} />;
    }
  };

  const getChannelColor = (channel) => {
    switch (channel) {
      case 'email':
        return 'bg-blue-600';
      case 'linkedin':
        return 'bg-purple-600';
      case 'voicemail':
        return 'bg-green-600';
      default:
        return 'bg-slate-600';
    }
  };

  const capitalizeFirst = (str) => {
    return str.charAt(0).toUpperCase() + str.slice(1);
  };

  if (loading) {
    return (
      <Layout user={user} onLogout={onLogout}>
        <div className="flex items-center justify-center h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="p-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <Button variant="outline" onClick={onBack} className="mb-6">
            <ArrowLeft size={16} className="mr-2" /> Back
          </Button>

          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 mb-2">Campaign Timeline</h1>
              <p className="text-slate-600">{campaign.campaign_name} • {campaign.stage} Campaign for {campaign.service}</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline">
                <FileDown size={16} className="mr-2" /> Export
              </Button>
              <Button className="bg-gradient-to-r from-indigo-600 to-blue-600">
                <Send size={16} className="mr-2" /> Send for Review
              </Button>
            </div>
          </div>

          {/* Drag Instructions */}
          <div className="mb-6 p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
            <p className="text-sm text-indigo-900 font-medium">
              💡 <strong>Tip:</strong> Drag items to reorder the sequence
            </p>
          </div>

          {/* Timeline */}
          <DragDropContext onDragEnd={handleDragEnd}>
            <Droppable droppableId="timeline">
              {(provided) => (
                <div
                  {...provided.droppableProps}
                  ref={provided.innerRef}
                  className="space-y-4"
                >
                  {sequence?.steps?.map((step, index) => (
                    <Draggable
                      key={`step-${step.step_number}`}
                      draggableId={`step-${step.step_number}`}
                      index={index}
                    >
                      {(provided, snapshot) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                          className={`flex gap-4 ${
                            snapshot.isDragging ? 'opacity-50' : ''
                          }`}
                        >
                          {/* Icon Column */}
                          <div className="flex flex-col items-center">
                            <div
                              className={`w-12 h-12 rounded-lg ${getChannelColor(
                                step.channel
                              )} flex items-center justify-center shadow-lg`}
                            >
                              {getChannelIcon(step.channel)}
                            </div>
                            {index < sequence.steps.length - 1 && (
                              <div className="w-0.5 h-full bg-slate-200 my-2"></div>
                            )}
                          </div>

                          {/* Content Column */}
                          <Card className="flex-1 p-6 bg-white border border-slate-200 shadow-md hover:shadow-lg transition-shadow">
                            <div className="flex items-start justify-between mb-3">
                              <div>
                                <p className="text-sm font-semibold text-slate-600 mb-1">
                                  Day {step.day}
                                </p>
                                <h4 className="text-lg font-bold text-slate-900">
                                  {capitalizeFirst(step.channel)}
                                </h4>
                              </div>
                              <div className="flex gap-2">
                                {step.content && (
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => handleEditContent(step)}
                                  >
                                    <Edit2 size={14} className="mr-1" /> Edit Draft
                                  </Button>
                                )}
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => handleGenerateContent(step.step_number)}
                                  disabled={generatingStep === step.step_number}
                                >
                                  {generatingStep === step.step_number ? (
                                    <>
                                      <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-indigo-600 mr-1"></div>
                                      Generating...
                                    </>
                                  ) : (
                                    <>
                                      <Sparkles size={14} className="mr-1" />
                                      {step.content ? 'Regenerate' : 'Generate'}
                                    </>
                                  )}
                                </Button>
                              </div>
                            </div>

                            {step.content ? (
                              <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                                <p className="text-sm text-slate-800 whitespace-pre-wrap">
                                  {step.content}
                                </p>
                              </div>
                            ) : (
                              <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 text-center">
                                <p className="text-sm text-slate-500 italic">
                                  Generating content with AI...
                                </p>
                              </div>
                            )}

                            {step.content && (
                              <div className="flex gap-2 mt-4">
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => {
                                    navigator.clipboard.writeText(step.content);
                                    toast.success('Copied to clipboard!');
                                  }}
                                >
                                  <Copy size={14} className="mr-1" /> Copy & Send
                                </Button>
                              </div>
                            )}
                          </Card>
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </DragDropContext>

          {/* Edit Dialog */}
          <Dialog open={!!editingStep} onOpenChange={() => setEditingStep(null)}>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>
                  Edit {editingStep && capitalizeFirst(editingStep.channel)} Content
                </DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <Textarea
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  rows={12}
                  className="font-mono text-sm"
                />
                <div className="flex gap-2">
                  <Button onClick={handleSaveEdit} className="flex-1">
                    Save Changes
                  </Button>
                  <Button variant="outline" onClick={() => setEditingStep(null)}>
                    Cancel
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>
    </Layout>
  );
};

export default CampaignTimeline;