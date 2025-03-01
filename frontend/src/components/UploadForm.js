import React, { useCallback } from 'react';
import { Box, Typography, Button, Paper } from '@mui/material';
import { useDropzone } from 'react-dropzone';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import axios from 'axios';

// Get the API URL from environment variables or use the default
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const UploadForm = ({ setLoading, setResult, setError, setFile, setFilePreview }) => {
  const onDrop = useCallback(acceptedFiles => {
    if (acceptedFiles.length === 0) {
      setError('Please upload a valid image or video file.');
      return;
    }

    const file = acceptedFiles[0];
    setFile(file);

    // Create a preview for the file
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = () => {
        setFilePreview({
          type: 'image',
          src: reader.result
        });
      };
      reader.readAsDataURL(file);
    } else if (file.type.startsWith('video/')) {
      setFilePreview({
        type: 'video',
        src: URL.createObjectURL(file)
      });
    }

    handleUpload(file);
  }, [setFile, setFilePreview, setError]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png'],
      'video/*': ['.mp4', '.mov', '.avi']
    },
    maxFiles: 1
  });

  const handleUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/api/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setResult(response.data.result);
    } catch (error) {
      console.error('Error uploading file:', error);
      setError(
        error.response?.data?.error || 
        'An error occurred while analyzing the file. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ mt: 2 }}>
      <Paper
        {...getRootProps()}
        className="dropzone"
        sx={{
          p: 5,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          backgroundColor: isDragActive ? 'rgba(63, 81, 181, 0.05)' : 'transparent',
          transition: 'all 0.3s ease'
        }}
      >
        <input {...getInputProps()} />
        <CloudUploadIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {isDragActive ? 'Drop the file here' : 'Drag & drop a file here'}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          or
        </Typography>
        <Button variant="contained" color="primary" component="span">
          Browse Files
        </Button>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          Supported formats: JPEG, PNG, MP4, MOV, AVI
        </Typography>
      </Paper>
    </Box>
  );
};

export default UploadForm; 