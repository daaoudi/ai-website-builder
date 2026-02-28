import React, { useState, useRef, useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { HexColorPicker } from 'react-colorful';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

const industries = [
  'Technology', 'Healthcare', 'Education', 'E-commerce',
  'Real Estate', 'Restaurant', 'Consulting', 'Creative Agency',
  'Legal', 'Construction', 'Travel', 'Fitness'
];

const tones = [
  'modern', 'minimal', 'luxury', 'playful', 'professional', 'bold', 'elegant'
];

const availablePages = [
  'home', 'about', 'services', 'contact', 'blog', 'portfolio', 'pricing', 'faq'
];

const ProjectForm = () => {
  const [activeColorPicker, setActiveColorPicker] = useState(null);
  const [loading, setLoading] = useState(false);
  const { token } = useAuth();
  const navigate = useNavigate();
  
  const colorPickerRefs = {
    primary: useRef(null),
    secondary: useRef(null),
    accent: useRef(null)
  };
  
  const { register, handleSubmit, control, setValue, watch } = useForm({
    defaultValues: {
      business_name: '',
      industry: 'Technology',
      domain: '',
      primary_color: '#3B82F6',
      secondary_color: '#10B981',
      accent_color: '#F59E0B',
      pages: ['home', 'about', 'services', 'contact'],
      tone: 'modern',
      features: '',
      cta_text: 'Get Started'
    }
  });

  const selectedPages = watch('pages', []);

  // Handle click outside to close color picker

useEffect(() => {
  const handleClickOutside = (event) => {
    if (activeColorPicker) {
      const ref = colorPickerRefs[activeColorPicker];
      if (ref.current && !ref.current.contains(event.target)) {
        setActiveColorPicker(null);
      }
    }
  };

  document.addEventListener('mousedown', handleClickOutside);
  return () => document.removeEventListener('mousedown', handleClickOutside);
}, [activeColorPicker, colorPickerRefs]); // Added colorPickerRefs to dependencies

  const handlePageToggle = (page) => {
    const current = selectedPages || [];
    const newPages = current.includes(page)
      ? current.filter(p => p !== page)
      : [...current, page];
    setValue('pages', newPages);
  };

  const onSubmit = async (data) => {
    setLoading(true);
    
    try {
      const featuresArray = data.features
        ? data.features.split(',').map(f => f.trim()).filter(f => f)
        : [];

      const projectData = {
        business_name: data.business_name,
        industry: data.industry,
        domain: data.domain || null,
        colors: {
          primary: data.primary_color,
          secondary: data.secondary_color,
          accent: data.accent_color
        },
        pages: selectedPages,
        tone: data.tone.toLowerCase(),
        language: 'en',
        features: featuresArray,
        cta_text: data.cta_text || 'Get Started',
        contact_info: {}
      };

      const response = await axios.post(
        'http://localhost:8000/api/projects',
        projectData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      toast.success('Project created successfully!');
      navigate(`/projects/${response.data.job_id}`);
      
    } catch (error) {
      console.error('Error creating project:', error.response?.data || error);
      toast.error(error.response?.data?.detail || 'Failed to create project');
    } finally {
      setLoading(false);
    }
  };

  const ColorPickerField = ({ label, name, colorPickerId }) => {
    const isOpen = activeColorPicker === colorPickerId;
    
    return (
      <div className="relative" ref={colorPickerRefs[colorPickerId]}>
        <label className="block text-xs text-gray-500 mb-1">{label}</label>
        <div className="flex items-center space-x-2">
          <Controller
            name={name}
            control={control}
            render={({ field }) => (
              <>
                <div
                  className="w-10 h-10 rounded border-2 border-gray-200 cursor-pointer shadow-sm hover:scale-105 transition-transform"
                  style={{ backgroundColor: field.value }}
                  onClick={(e) => {
                    e.stopPropagation();
                    setActiveColorPicker(isOpen ? null : colorPickerId);
                  }}
                />
                <input
                  type="text"
                  value={field.value}
                  onChange={(e) => field.onChange(e.target.value)}
                  className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 font-mono text-sm px-3 py-2"
                  placeholder="#000000"
                />
              </>
            )}
          />
        </div>
        
        {isOpen && (
          <div className="absolute z-50 mt-2 bg-white p-3 rounded-lg shadow-xl border">
            <Controller
              name={name}
              control={control}
              render={({ field }) => (
                <HexColorPicker 
                  color={field.value} 
                  onChange={(newColor) => {
                    field.onChange(newColor);
                    // Don't close the picker while selecting colors
                  }} 
                />
              )}
            />
          </div>
        )}
      </div>
    );
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 bg-white p-6 rounded-lg shadow max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-900">Create New Project</h2>
      
      {/* Business Name */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Business Name *
        </label>
        <input
          type="text"
          {...register('business_name', { required: true })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Acme Inc."
        />
      </div>

      {/* Industry */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Industry
        </label>
        <select
          {...register('industry')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {industries.map(industry => (
            <option key={industry}>{industry}</option>
          ))}
        </select>
      </div>

      {/* Domain (Optional) */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Custom Domain (Optional)
        </label>
        <input
          type="text"
          {...register('domain')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="example.com"
        />
      </div>

      {/* Pages */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Pages to Include
        </label>
        <div className="grid grid-cols-2 gap-2">
          {availablePages.map(page => (
            <label key={page} className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={selectedPages?.includes(page)}
                onChange={() => handlePageToggle(page)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700 capitalize">{page}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Tone */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Design Tone
        </label>
        <select
          {...register('tone')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {tones.map(tone => (
            <option key={tone} value={tone}>{tone.charAt(0).toUpperCase() + tone.slice(1)}</option>
          ))}
        </select>
      </div>

      {/* Colors */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Brand Colors
        </label>
        <div className="space-y-4">
          <ColorPickerField
            label="Primary"
            name="primary_color"
            colorPickerId="primary"
          />
          <ColorPickerField
            label="Secondary"
            name="secondary_color"
            colorPickerId="secondary"
          />
          <ColorPickerField
            label="Accent"
            name="accent_color"
            colorPickerId="accent"
          />
        </div>
      </div>

      {/* Features */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Features (comma separated)
        </label>
        <input
          type="text"
          {...register('features')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="contact form, newsletter, gallery, testimonials"
        />
      </div>

      {/* CTA Text */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Call to Action Text
        </label>
        <input
          type="text"
          {...register('cta_text')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Get Started"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Creating Project...' : 'Generate Website'}
      </button>
    </form>
  );
};

export default ProjectForm;