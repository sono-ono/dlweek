import React, { useState } from 'react';
import { Container, Typography, Box, Paper, AppBar, Toolbar, Button } from '@mui/material';
import UploadForm from './components/UploadForm';
import AnalysisResult from './components/AnalysisResult';
import LoadingState from './components/LoadingState';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [file, setFile] = useState(null);
  const [filePreview, setFilePreview] = useState(null);

  const handleReset = () => {
    setResult(null);
    setLoading(false);
    setError(null);
    setFile(null);
    setFilePreview(null);
  };

  return (
    <div className="App">
      <AppBar position="static" elevation={0}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Deepfake Detector
          </Typography>
        </Toolbar>
      </AppBar>
      
      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        <Paper 
          elevation={3} 
          sx={{ 
            p: 4, 
            borderRadius: 2,
            background: 'linear-gradient(to right bottom, #ffffff, #f8f9fa)'
          }}
        >
          <Box sx={{ mb: 4, textAlign: 'center' }}>
            <Typography variant="h4" component="h1" gutterBottom>
              Deepfake Analysis Tool
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Upload an image or video to analyze for potential AI manipulation
            </Typography>
          </Box>

          {!loading && !result && (
            <UploadForm 
              setLoading={setLoading} 
              setResult={setResult} 
              setError={setError}
              setFile={setFile}
              setFilePreview={setFilePreview}
            />
          )}

          {loading && <LoadingState />}

          {error && (
            <Box sx={{ mt: 3, textAlign: 'center' }}>
              <Typography color="error" variant="body1">
                {error}
              </Typography>
              <Button 
                variant="outlined" 
                color="primary" 
                onClick={handleReset}
                sx={{ mt: 2 }}
              >
                Try Again
              </Button>
            </Box>
          )}

          {result && (
            <>
              <AnalysisResult result={result} filePreview={filePreview} file={file} />
              <Box sx={{ mt: 3, textAlign: 'center' }}>
                <Button 
                  variant="contained" 
                  color="primary" 
                  onClick={handleReset}
                >
                  Analyze Another File
                </Button>
              </Box>
            </>
          )}
        </Paper>
      </Container>
    </div>
  );
}

export default App; 