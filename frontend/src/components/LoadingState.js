import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

const LoadingState = () => {
  return (
    <Box className="loading-container">
      <CircularProgress size={60} thickness={4} />
      <Typography variant="h6" sx={{ mt: 3 }}>
        Analyzing your media...
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
        This may take a few moments as we process your file through multiple AI models.
      </Typography>
    </Box>
  );
};

export default LoadingState; 