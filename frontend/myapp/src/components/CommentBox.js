import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Link } from 'react-router-dom';
import { 
  ChatBubbleLeftIcon, 
  ChartBarIcon,
  FaceSmileIcon,
  FaceFrownIcon,
  MinusCircleIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const CommentBox = ({ projectId }) => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [stats, setStats] = useState({
    positive: 0,
    neutral: 0,
    negative: 0,
    total: 0
  });
  
  const { token } = useAuth();

  const fetchComments = useCallback(async () => {
    console.log('📊 Fetching comments for project:', projectId);
    setLoading(true);
    try {
      const response = await axios.get(
        `http://localhost:8000/api/projects/${projectId}/sentiment`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      
      console.log('✅ Sentiment data received:', response.data);
      
      if (response.data.recent) {
        setComments(response.data.recent);
      }
      
      if (response.data.overall) {
        setStats({
          positive: response.data.overall.positive || 0,
          neutral: response.data.overall.neutral || 0,
          negative: response.data.overall.negative || 0,
          total: (response.data.overall.positive || 0) + 
                 (response.data.overall.neutral || 0) + 
                 (response.data.overall.negative || 0)
        });
      }
    } catch (error) {
      console.error('❌ Failed to fetch comments:', error);
      toast.error('Failed to load comments');
    } finally {
      setLoading(false);
    }
  }, [projectId, token]);

  useEffect(() => {
    fetchComments();
  }, [fetchComments]);

  const handleSubmitComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    const commentText = newComment.trim();
    console.log('📝 Submitting comment:', commentText);
    
    setSubmitting(true);
    try {
      const response = await axios.post(
        `http://localhost:8000/api/projects/${projectId}/comments`,
        { text: commentText },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      console.log('✅ Comment added successfully:', response.data);
      
      setNewComment('');
      toast.success('Comment added! Analyzing sentiment...');
      
      // Immediately fetch comments to show the new comment
      await fetchComments();
      
      // Then fetch again after 3 seconds to get the sentiment
      setTimeout(() => {
        fetchComments();
      }, 3000);
      
    } catch (error) {
      console.error('❌ Failed to add comment:', error);
      console.error('Error response:', error.response?.data);
      toast.error(error.response?.data?.detail || 'Failed to add comment');
    } finally {
      setSubmitting(false);
    }
  };

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return <FaceSmileIcon className="h-5 w-5 text-green-500" />;
      case 'negative':
        return <FaceFrownIcon className="h-5 w-5 text-red-500" />;
      case 'neutral':
        return <MinusCircleIcon className="h-5 w-5 text-yellow-500" />;
      default:
        return <ChatBubbleLeftIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      {/* Header with Stats */}
      <div className="bg-gray-50 border-b px-6 py-4">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-medium">Customer Feedback</h3>
          <Link
            to={`/projects/${projectId}/sentiment`}
            className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800"
          >
            <ChartBarIcon className="h-4 w-4 mr-1" />
            Full Dashboard
          </Link>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-3 gap-4 mt-4">
          <div className="bg-green-50 rounded-lg p-3">
            <div className="flex items-center">
              <FaceSmileIcon className="h-5 w-5 text-green-500" />
              <span className="ml-2 text-sm text-gray-600">Positive</span>
            </div>
            <p className="text-2xl font-semibold text-green-600 mt-1">
              {stats.positive}
            </p>
          </div>
          <div className="bg-yellow-50 rounded-lg p-3">
            <div className="flex items-center">
              <MinusCircleIcon className="h-5 w-5 text-yellow-500" />
              <span className="ml-2 text-sm text-gray-600">Neutral</span>
            </div>
            <p className="text-2xl font-semibold text-yellow-600 mt-1">
              {stats.neutral}
            </p>
          </div>
          <div className="bg-red-50 rounded-lg p-3">
            <div className="flex items-center">
              <FaceFrownIcon className="h-5 w-5 text-red-500" />
              <span className="ml-2 text-sm text-gray-600">Negative</span>
            </div>
            <p className="text-2xl font-semibold text-red-600 mt-1">
              {stats.negative}
            </p>
          </div>
        </div>
      </div>

      {/* Comment Input */}
      <div className="p-6 border-b">
        <form onSubmit={handleSubmitComment}>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Add a Comment
          </label>
          <div className="flex space-x-2">
            <input
              type="text"
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Enter customer feedback or review..."
              className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              disabled={submitting}
            />
            <button
              type="submit"
              disabled={submitting || !newComment.trim()}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {submitting ? 'Adding...' : 'Add'}
            </button>
          </div>
        </form>
      </div>

      {/* Comments List */}
      <div className="p-6">
        <h4 className="text-sm font-medium text-gray-700 mb-4">Recent Comments</h4>
        
        {loading ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : comments.length === 0 ? (
          <p className="text-center text-gray-500 py-8">
            No comments yet. Add your first comment above.
          </p>
        ) : (
          <div className="space-y-4">
            {comments.map((comment) => (
              <div
                key={comment.id}
                className="border rounded-lg p-4 hover:shadow-sm transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm text-gray-900">{comment.text}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {comment.created_at ? new Date(comment.created_at).toLocaleString() : 'Just now'}
                    </p>
                  </div>
                  <div className="ml-4 flex items-center space-x-2">
                    {getSentimentIcon(comment.sentiment)}
                    {comment.confidence && (
                      <span className="text-xs text-gray-500">
                        {(comment.confidence * 100).toFixed(0)}%
                      </span>
                    )}
                    {!comment.sentiment && (
                      <span className="text-xs text-gray-400 italic">Analyzing...</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default CommentBox;