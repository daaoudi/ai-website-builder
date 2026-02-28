// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import ProjectDetails from './pages/ProjectDetails';
import SentimentDashboard from './pages/SentimentDashboard';
import Settings from './pages/Settings';
import ProjectForm from './components/ProjectForm';
import WebsitePreview from './pages/WebsitePreview'; // Import the new preview page

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/" element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          } />
          
          <Route path="/projects/new" element={
            <PrivateRoute>
              <ProjectForm />
            </PrivateRoute>
          } />
          
          <Route path="/projects/:id" element={
            <PrivateRoute>
              <ProjectDetails />
            </PrivateRoute>
          } />
          
          <Route path="/projects/:id/sentiment" element={
            <PrivateRoute>
              <SentimentDashboard />
            </PrivateRoute>
          } />
          
          {/* Add the preview route */}
          <Route path="/preview/:id" element={
            <PrivateRoute>
              <WebsitePreview />
            </PrivateRoute>
          } />
          
          <Route path="/settings" element={
            <PrivateRoute>
              <Settings />
            </PrivateRoute>
          } />
          
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;