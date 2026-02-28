import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import Navbar from '../components/Navbar';
import Preview from '../components/Preview';
import CommentBox from '../components/CommentBox';
import { Tab } from '@headlessui/react';
import { ArrowPathIcon, CloudArrowUpIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const ProjectDetails = () => {
  const { id } = useParams();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [publishing, setPublishing] = useState(false);
  const { token } = useAuth();

  useEffect(() => {
    fetchProject();
    
    // Poll for updates if generating
    const interval = setInterval(fetchProject, 3000);
    return () => clearInterval(interval);
  }, [id]);

  const fetchProject = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/projects/${id}/status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProject(response.data);
    } catch (error) {
      console.error('Failed to fetch project:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePublish = async () => {
    setPublishing(true);
    try {
      await axios.post(`http://localhost:8000/api/projects/${id}/publish`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Website published successfully!');
    } catch (error) {
      toast.error('Failed to publish website');
    } finally {
      setPublishing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <ArrowPathIcon className="h-12 w-12 text-blue-500 animate-spin mx-auto" />
            <p className="mt-4 text-gray-600">Loading project...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="px-4 sm:px-0 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">{project?.name}</h1>
              <p className="text-sm text-gray-500">
                Status: <span className={`font-medium ${
                  project?.status === 'completed' ? 'text-green-600' :
                  project?.status === 'failed' ? 'text-red-600' :
                  'text-yellow-600'
                }`}>{project?.status}</span>
              </p>
            </div>
            {project?.status === 'completed' && (
              <button
                onClick={handlePublish}
                disabled={publishing}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
              >
                <CloudArrowUpIcon className="h-5 w-5 mr-2" />
                {publishing ? 'Publishing...' : 'Publish Website'}
              </button>
            )}
          </div>
        </div>

        {/* Status Banner */}
        {project?.status === 'generating' && (
          <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
            <div className="flex">
              <ArrowPathIcon className="h-5 w-5 text-blue-400 animate-spin" />
              <div className="ml-3">
                <p className="text-sm text-blue-700">
                  Your website is being generated. This may take up to a minute...
                </p>
              </div>
            </div>
          </div>
        )}

        {project?.status === 'failed' && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
            <p className="text-sm text-red-700">
              Generation failed. Please try again or contact support.
            </p>
          </div>
        )}

        {/* Main Content */}
        {project?.status === 'completed' && (
          <Tab.Group>
            <Tab.List className="flex space-x-1 rounded-xl bg-blue-900/20 p-1 mb-6">
              <Tab className={({ selected }) =>
                `w-full rounded-lg py-2.5 text-sm font-medium leading-5
                 ${selected ? 'bg-white text-blue-700 shadow' : 'text-gray-600 hover:bg-white/[0.12] hover:text-blue-600'}`
              }>
                Preview & Edit
              </Tab>
              <Tab className={({ selected }) =>
                `w-full rounded-lg py-2.5 text-sm font-medium leading-5
                 ${selected ? 'bg-white text-blue-700 shadow' : 'text-gray-600 hover:bg-white/[0.12] hover:text-blue-600'}`
              }>
                Comments & Sentiment
              </Tab>
            </Tab.List>
            
            <Tab.Panels>
              <Tab.Panel>
                <Preview projectId={id} previewUrl={project?.preview_url} />
              </Tab.Panel>
              <Tab.Panel>
                <CommentBox projectId={id} />
              </Tab.Panel>
            </Tab.Panels>
          </Tab.Group>
        )}
      </main>
    </div>
  );
};

export default ProjectDetails;