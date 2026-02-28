import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { ArrowLeftIcon, CodeBracketIcon, DevicePhoneMobileIcon } from '@heroicons/react/24/outline';
import Preview from '../components/Preview';
import toast from 'react-hot-toast';

const WebsitePreview = () => {
  const { id } = useParams();
  const { token } = useAuth();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [previewUrl, setPreviewUrl] = useState('');
  const [viewMode, setViewMode] = useState('desktop'); // 'desktop' or 'mobile'
  const [showCode, setShowCode] = useState(false);
  const [generatedHtml, setGeneratedHtml] = useState('');

  useEffect(() => {
    fetchProject();
  }, [id]);

  const fetchProject = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/projects/${id}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      console.log('Project data received:', response.data);
      setProject(response.data);
      
      // Use the preview_url from the backend (should be a data URL from Groq)
      if (response.data.preview_url) {
        setPreviewUrl(response.data.preview_url);
        
        // Fetch the HTML content for the code view
        if (response.data.preview_url.startsWith('data:')) {
          // Extract base64 content from data URL
          const base64Content = response.data.preview_url.split(',')[1];
          try {
            const htmlContent = atob(base64Content);
            setGeneratedHtml(htmlContent);
          } catch (e) {
            console.error('Error decoding base64:', e);
          }
        }
      }
    } catch (error) {
      console.error('Error fetching project:', error);
      toast.error('Failed to load project');
    } finally {
      setLoading(false);
    }
  };

  const getPreviewWidth = () => {
    switch(viewMode) {
      case 'mobile':
        return 'w-[375px]';
      case 'tablet':
        return 'w-[768px]';
      default:
        return 'w-full';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900">Project not found</h2>
        <Link to="/dashboard" className="mt-4 inline-block text-blue-600 hover:underline">
          Back to Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Preview Toolbar */}
      <div className="bg-white shadow-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center space-x-4">
              <Link
                to={`/projects/${id}`}
                className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900"
              >
                <ArrowLeftIcon className="h-4 w-4 mr-1" />
                Back to Project
              </Link>
              <span className="text-sm font-medium text-gray-900">
                Preview: {project.name}
              </span>
            </div>
            
            <div className="flex items-center space-x-2">
              {/* View Mode Toggle */}
              <div className="flex items-center bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setViewMode('desktop')}
                  className={`px-3 py-1 rounded-md text-sm flex items-center ${
                    viewMode === 'desktop' ? 'bg-white shadow' : 'text-gray-600'
                  }`}
                >
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20.25 15 20.25 14.25 17M9 17H5.5C4.836 17 4.25 16.414 4.25 15.75V5.5C4.25 4.836 4.836 4.25 5.5 4.25h13c.664 0 1.25.586 1.25 1.25v10.25c0 .664-.586 1.25-1.25 1.25H15" />
                  </svg>
                  Desktop
                </button>
                <button
                  onClick={() => setViewMode('tablet')}
                  className={`px-3 py-1 rounded-md text-sm flex items-center ${
                    viewMode === 'tablet' ? 'bg-white shadow' : 'text-gray-600'
                  }`}
                >
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M7 21h10c1.105 0 2-.895 2-2V5c0-1.105-.895-2-2-2H7c-1.105 0-2 .895-2 2v14c0 1.105.895 2 2 2z" />
                  </svg>
                  Tablet
                </button>
                <button
                  onClick={() => setViewMode('mobile')}
                  className={`px-3 py-1 rounded-md text-sm flex items-center ${
                    viewMode === 'mobile' ? 'bg-white shadow' : 'text-gray-600'
                  }`}
                >
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                  Mobile
                </button>
              </div>

              {/* Code View Toggle */}
              <button
                onClick={() => setShowCode(!showCode)}
                className={`inline-flex items-center px-3 py-1 rounded-md text-sm ${
                  showCode ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'
                }`}
              >
                <CodeBracketIcon className="h-4 w-4 mr-1" />
                {showCode ? 'Hide Code' : 'View Code'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {showCode ? (
          <div className="bg-gray-900 rounded-lg overflow-hidden">
            <div className="bg-gray-800 px-4 py-2 flex justify-between items-center">
              <span className="text-white text-sm font-mono">Generated HTML</span>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(generatedHtml);
                  toast.success('Code copied to clipboard!');
                }}
                className="text-gray-300 hover:text-white text-sm"
              >
                Copy Code
              </button>
            </div>
            <pre className="p-4 overflow-auto max-h-[600px] text-sm">
              <code className="text-green-400 font-mono whitespace-pre-wrap">
                {generatedHtml || '<!-- No HTML code available -->'}
              </code>
            </pre>
          </div>
        ) : (
          <div className="flex justify-center">
            <div className={`${getPreviewWidth()} transition-all duration-300`}>
              <div className="bg-white rounded-lg shadow-lg overflow-hidden">
                {viewMode !== 'desktop' && (
                  <div className="bg-gray-100 px-4 py-2 border-b flex items-center justify-center">
                    <div className="flex space-x-2">
                      <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                      <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    </div>
                    <span className="ml-4 text-xs text-gray-500">
                      {viewMode === 'mobile' ? 'Mobile View' : 'Tablet View'}
                    </span>
                  </div>
                )}
                <Preview projectId={id} previewUrl={previewUrl} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Project Info */}
      {project && project.brief && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Project Details</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Industry:</span>
                <span className="ml-2 text-gray-900">{project.brief.industry}</span>
              </div>
              <div>
                <span className="text-gray-500">Tone:</span>
                <span className="ml-2 text-gray-900 capitalize">{project.brief.tone}</span>
              </div>
              <div>
                <span className="text-gray-500">Pages:</span>
                <span className="ml-2 text-gray-900">{project.brief.pages?.length || 0}</span>
              </div>
              <div>
                <span className="text-gray-500">Colors:</span>
                <div className="inline-flex ml-2 space-x-1">
                  {project.brief.colors && (
                    <>
                      <div className="w-4 h-4 rounded-full" style={{ backgroundColor: project.brief.colors.primary }} title="Primary"></div>
                      <div className="w-4 h-4 rounded-full" style={{ backgroundColor: project.brief.colors.secondary }} title="Secondary"></div>
                      <div className="w-4 h-4 rounded-full" style={{ backgroundColor: project.brief.colors.accent }} title="Accent"></div>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WebsitePreview;