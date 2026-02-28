import React, { useState, useEffect } from 'react';
import Iframe from 'react-iframe';
import { PencilIcon, ArrowPathIcon, ArrowPathRoundedSquareIcon } from '@heroicons/react/24/outline';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const Preview = ({ projectId, previewUrl }) => {
  const [editMode, setEditMode] = useState(false);
  const [selectedElement, setSelectedElement] = useState(null);
  const [loading, setLoading] = useState(false);
  const [iframeKey, setIframeKey] = useState(Date.now());
  const [iframeLoading, setIframeLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);
  const { token } = useAuth();

  // Reset iframe loading state when previewUrl changes
  useEffect(() => {
    setIframeLoading(true);
    setLoadError(false);
    setIframeKey(Date.now());
  }, [previewUrl]);

  const handleEdit = () => {
    setEditMode(!editMode);
  };

  const handleRefresh = () => {
    setIframeLoading(true);
    setLoadError(false);
    setIframeKey(Date.now());
  };

  const handleIframeLoad = () => {
    setIframeLoading(false);
  };

  const handleIframeError = () => {
    setIframeLoading(false);
    setLoadError(true);
    console.error('Failed to load iframe content');
  };

  // Check if previewUrl is a data URL (AI-generated content)
  const isDataUrl = previewUrl?.startsWith('data:');

  // Check if previewUrl is a local URL (should use AI-generated content instead)
  const isLocalUrl = previewUrl?.includes('localhost:3000/preview/');

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      {/* Toolbar */}
      <div className="bg-gray-50 border-b px-4 py-2 flex justify-between items-center">
        <h3 className="text-sm font-medium text-gray-700">Website Preview</h3>
        <div className="flex space-x-2">
          <button
            onClick={handleEdit}
            className={`inline-flex items-center px-3 py-1 rounded text-sm ${
              editMode 
                ? 'bg-blue-100 text-blue-700' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <PencilIcon className="h-4 w-4 mr-1" />
            {editMode ? 'Exit Edit Mode' : 'Edit Mode'}
          </button>
          <button
            onClick={handleRefresh}
            className="inline-flex items-center px-3 py-1 rounded text-sm bg-gray-100 text-gray-700 hover:bg-gray-200"
            title="Refresh preview"
          >
            <ArrowPathIcon className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Preview Area */}
      <div className="relative bg-gray-100 min-h-[600px] flex items-center justify-center">
        {iframeLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 z-10">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-sm text-gray-600">Loading AI-generated preview...</p>
            </div>
          </div>
        )}

        {loadError && (
          <div className="absolute inset-0 flex items-center justify-center bg-white z-10">
            <div className="text-center p-8">
              <div className="text-red-500 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Failed to load preview</h3>
              <p className="text-gray-500 mb-4">The preview content could not be loaded.</p>
              <button
                onClick={handleRefresh}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                <ArrowPathRoundedSquareIcon className="h-4 w-4 mr-2" />
                Try Again
              </button>
            </div>
          </div>
        )}

        {/* AI-Generated Content (Data URL) */}
        {isDataUrl && !isLocalUrl && (
          <iframe
            key={iframeKey}
            src={previewUrl}
            width="100%"
            height="600px"
            className="border-0"
            title={`AI Generated Website - ${projectId}`}
            sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
            onLoad={handleIframeLoad}
            onError={handleIframeError}
          />
        )}

        {/* External URL */}
        {!isDataUrl && !isLocalUrl && previewUrl && (
          <Iframe
            url={previewUrl}
            width="100%"
            height="600px"
            id={`website-preview-${projectId}`}
            className="border-0"
            display="block"
            position="relative"
            sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
            onLoad={handleIframeLoad}
            onError={handleIframeError}
          />
        )}

        {/* No preview URL available */}
        {!previewUrl && !loading && !loadError && (
          <div className="text-center p-12">
            <div className="text-gray-400 mb-4">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20.25 15 20.25 14.25 17M9 17H5.5C4.836 17 4.25 16.414 4.25 15.75V5.5C4.25 4.836 4.836 4.25 5.5 4.25h13c.664 0 1.25.586 1.25 1.25v10.25c0 .664-.586 1.25-1.25 1.25H15" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Preview Available</h3>
            <p className="text-gray-500">The website preview is not yet generated.</p>
          </div>
        )}

        {/* Edit Overlay */}
        {editMode && (
          <div className="absolute inset-0 bg-blue-500/10 pointer-events-none">
            <div className="absolute top-4 left-4 bg-white p-4 rounded-lg shadow-lg pointer-events-auto">
              <h4 className="text-sm font-medium mb-2">Edit Mode</h4>
              <p className="text-xs text-gray-500">
                Click on any element to edit its content
              </p>
              <div className="mt-3 space-y-2">
                <button className="w-full text-left text-sm px-2 py-1 hover:bg-gray-100 rounded">
                  Edit Text
                </button>
                <button className="w-full text-left text-sm px-2 py-1 hover:bg-gray-100 rounded">
                  Change Color
                </button>
                <button className="w-full text-left text-sm px-2 py-1 hover:bg-gray-100 rounded">
                  Reorder Section
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Preview Info */}
      {previewUrl && (
        <div className="bg-gray-50 border-t px-4 py-2 text-xs text-gray-500 flex justify-between items-center">
          <span>
            {isDataUrl ? 'AI-Generated Preview' : 'External Preview'}
          </span>
          {isDataUrl && (
            <span className="text-green-600 flex items-center">
              <span className="w-2 h-2 bg-green-600 rounded-full mr-1"></span>
              Generated with  AI
            </span>
          )}
        </div>
      )}
    </div>
  );
};

export default Preview;