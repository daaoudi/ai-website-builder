import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { 
  ChartBarIcon, 
  FaceSmileIcon, 
  FaceFrownIcon, 
  MinusCircleIcon,  // Using MinusCircleIcon instead of FaceIcon
  ArrowLeftIcon,
  ClockIcon,
  ChatBubbleLeftIcon,
  TagIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const SentimentDashboard = () => {
  const { projectId } = useParams();
  const { token } = useAuth();
  
  const [loading, setLoading] = useState(true);
  const [project, setProject] = useState(null);
  const [sentimentData, setSentimentData] = useState({
    overall: {
      positive: 0,
      neutral: 0,
      negative: 0,
      total: 0
    },
    recent: [],
    trends: [],
    topKeywords: []
  });
  const [timeRange, setTimeRange] = useState('week');
  const [selectedSentiment, setSelectedSentiment] = useState('all');

  useEffect(() => {
    fetchProjectData();
    fetchSentimentData();
  }, [projectId, timeRange]);

  const fetchProjectData = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/projects/${projectId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setProject(response.data);
    } catch (error) {
      console.error('Failed to fetch project:', error);
      toast.error('Failed to load project details');
    }
  };

  const fetchSentimentData = async () => {
    setLoading(true);
    try {
      const response = await axios.get(
        `http://localhost:8000/api/projects/${projectId}/sentiment?range=${timeRange}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setSentimentData({
        overall: response.data.overall || {
          positive: 0,
          neutral: 0,
          negative: 0,
          total: 0
        },
        recent: response.data.recent || [],
        trends: response.data.trends || [],
        topKeywords: response.data.topKeywords || []
      });
    } catch (error) {
      console.error('Failed to fetch sentiment data:', error);
      toast.error('Failed to load sentiment data');
    } finally {
      setLoading(false);
    }
  };

  const getSentimentIcon = (sentiment, className = 'h-5 w-5') => {
    switch (sentiment) {
      case 'positive':
        return <FaceSmileIcon className={`${className} text-green-500`} />;
      case 'negative':
        return <FaceFrownIcon className={`${className} text-red-500`} />;
      case 'neutral':
        return <MinusCircleIcon className={`${className} text-yellow-500`} />;  // Changed from FaceIcon
      default:
        return null;
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return 'text-green-600 bg-green-100';
      case 'negative':
        return 'text-red-600 bg-red-100';
      case 'neutral':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getSentimentBadge = (sentiment) => {
    const colors = {
      positive: 'bg-green-100 text-green-800',
      negative: 'bg-red-100 text-red-800',
      neutral: 'bg-yellow-100 text-yellow-800'
    };
    return colors[sentiment] || 'bg-gray-100 text-gray-800';
  };

  const filteredComments = sentimentData.recent.filter(comment => {
    if (selectedSentiment === 'all') return true;
    return comment.sentiment === selectedSentiment;
  });

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link
                to={`/projects/${projectId}`}
                className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900"
              >
                <ArrowLeftIcon className="h-4 w-4 mr-1" />
                Back to Project
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">
                Sentiment Analysis Dashboard
              </h1>
            </div>
            
            {/* Time Range Selector */}
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="day">Last 24 Hours</option>
              <option value="week">Last Week</option>
              <option value="month">Last Month</option>
              <option value="year">Last Year</option>
              <option value="all">All Time</option>
            </select>
          </div>
          
          {project && (
            <p className="mt-2 text-sm text-gray-600">
              {project.name} • {project.industry || 'No industry specified'}
            </p>
          )}
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-full">
                <ChatBubbleLeftIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Comments</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {sentimentData.overall.total}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-full">
                <FaceSmileIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Positive</p>
                <p className="text-2xl font-semibold text-green-600">
                  {sentimentData.overall.positive}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 bg-yellow-100 rounded-full">
                <MinusCircleIcon className="h-6 w-6 text-yellow-600" />  {/* Changed from FaceIcon */}
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Neutral</p>
                <p className="text-2xl font-semibold text-yellow-600">
                  {sentimentData.overall.neutral}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 bg-red-100 rounded-full">
                <FaceFrownIcon className="h-6 w-6 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Negative</p>
                <p className="text-2xl font-semibold text-red-600">
                  {sentimentData.overall.negative}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Sentiment Distribution Chart */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Sentiment Distribution</h2>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-green-600">Positive</span>
                  <span className="text-sm text-gray-600">
                    {sentimentData.overall.positive} comments
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div 
                    className="bg-green-600 h-2.5 rounded-full" 
                    style={{ 
                      width: `${sentimentData.overall.total > 0 
                        ? (sentimentData.overall.positive / sentimentData.overall.total) * 100 
                        : 0}%` 
                    }}
                  ></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-yellow-600">Neutral</span>
                  <span className="text-sm text-gray-600">
                    {sentimentData.overall.neutral} comments
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div 
                    className="bg-yellow-600 h-2.5 rounded-full" 
                    style={{ 
                      width: `${sentimentData.overall.total > 0 
                        ? (sentimentData.overall.neutral / sentimentData.overall.total) * 100 
                        : 0}%` 
                    }}
                  ></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-red-600">Negative</span>
                  <span className="text-sm text-gray-600">
                    {sentimentData.overall.negative} comments
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div 
                    className="bg-red-600 h-2.5 rounded-full" 
                    style={{ 
                      width: `${sentimentData.overall.total > 0 
                        ? (sentimentData.overall.negative / sentimentData.overall.total) * 100 
                        : 0}%` 
                    }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          {/* Top Keywords */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Top Keywords</h2>
            <div className="space-y-3">
              {sentimentData.topKeywords.map((keyword, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <TagIcon className="h-4 w-4 text-gray-400 mr-2" />
                    <span className="text-sm text-gray-700">{keyword.word}</span>
                  </div>
                  <span className="text-sm font-medium text-gray-900">
                    {keyword.count}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Comments */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium text-gray-900">Recent Comments</h2>
              
              {/* Sentiment Filter */}
              <select
                value={selectedSentiment}
                onChange={(e) => setSelectedSentiment(e.target.value)}
                className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
              >
                <option value="all">All Sentiments</option>
                <option value="positive">Positive Only</option>
                <option value="neutral">Neutral Only</option>
                <option value="negative">Negative Only</option>
              </select>
            </div>
          </div>

          {filteredComments.length === 0 ? (
            <div className="text-center py-12">
              <ChatBubbleLeftIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No comments</h3>
              <p className="mt-1 text-sm text-gray-500">
                {selectedSentiment !== 'all' 
                  ? `No ${selectedSentiment} comments found` 
                  : 'No comments have been added yet'}
              </p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {filteredComments.map((comment) => (
                <div key={comment.id} className="px-6 py-4 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm text-gray-900">{comment.text}</p>
                      <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                        <span className="flex items-center">
                          <ClockIcon className="h-3 w-3 mr-1" />
                          {new Date(comment.created_at).toLocaleString()}
                        </span>
                        {comment.confidence && (
                          <span>
                            Confidence: {(comment.confidence * 100).toFixed(0)}%
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="ml-4 flex items-center">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getSentimentBadge(comment.sentiment)}`}>
                        {comment.sentiment || 'pending'}
                      </span>
                      {getSentimentIcon(comment.sentiment, 'h-5 w-5 ml-2')}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SentimentDashboard;