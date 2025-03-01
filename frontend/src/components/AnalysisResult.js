import React from 'react';
import { Box, Typography, Paper, Divider, Card, CardContent, Grid } from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HelpIcon from '@mui/icons-material/Help';
import ConfidenceChart from './ConfidenceChart';

const AnalysisResult = ({ result, filePreview, file }) => {
  // Extract structured analysis and assessment sections if they exist
  const structuredAnalysisMatch = result.match(/<structured_analysis>([\s\S]*?)<\/structured_analysis>/);
  const assessmentMatch = result.match(/<assessment>([\s\S]*?)<\/assessment>/);

  // Extract likelihood from assessment if it exists
  let likelihood = "Unsure";
  let maliciousIntent = "Unsure";
  
  if (assessmentMatch) {
    const likelihoodMatch = assessmentMatch[1].match(/Likelihood of AI generation\/manipulation: (High|Low|Unsure)/);
    if (likelihoodMatch) {
      likelihood = likelihoodMatch[1];
    }
    
    const maliciousMatch = assessmentMatch[1].match(/Potential malicious intent: (Yes|No|Unsure)/);
    if (maliciousMatch) {
      maliciousIntent = maliciousMatch[1];
    }
  }

  // Extract probability from the result
  let probability = 0.5; // Default to 50% if not found
  let isFake = false;
  
  // First, determine if the content is fake or real based on the result text
  if (result.includes("high likelihood of this media being AI-generated") || 
      result.includes("deemed as AI-generated")) {
    isFake = true;
  } else if (result.includes("probably real") || result.includes("passed the AI detection")) {
    isFake = false;
  } else if (likelihood === "High") {
    isFake = true;
  } else if (likelihood === "Low") {
    isFake = false;
  }
  
  // Now extract the probability value
  // Try to find the exact probability pattern
  const probMatch = result.match(/probability (?:of it being real )?is (\d+\.\d+)/i);
  if (probMatch && probMatch[1]) {
    probability = parseFloat(probMatch[1]);
    
    // If the content is fake but the probability is "of being real", we need to invert it
    if (isFake && result.includes("probability of it being real")) {
      probability = 1 - probability;
    }
  } else {
    // If we couldn't find the probability, try to extract it from other patterns
    const percentMatch = result.match(/(\d+)%/);
    if (percentMatch && percentMatch[1]) {
      probability = parseInt(percentMatch[1]) / 100;
    } else {
      // If we still couldn't find a probability, assign a default based on fake/real status
      probability = isFake ? 0.8 : 0.8; // High confidence in either case
    }
  }

  // Ensure probability is within valid range
  probability = Math.max(0, Math.min(1, probability));

  // Determine icon and color based on likelihood
  let statusIcon;
  let statusColor;
  
  switch (likelihood) {
    case 'High':
      statusIcon = <WarningIcon fontSize="large" sx={{ color: 'error.main' }} />;
      statusColor = 'error.main';
      break;
    case 'Low':
      statusIcon = <CheckCircleIcon fontSize="large" sx={{ color: 'success.main' }} />;
      statusColor = 'success.main';
      break;
    default:
      statusIcon = <HelpIcon fontSize="large" sx={{ color: 'info.main' }} />;
      statusColor = 'info.main';
  }

  return (
    <Box sx={{ mt: 3 }}>
      {/* File Preview */}
      {filePreview && (
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'center' }}>
          {filePreview.type === 'image' ? (
            <img 
              src={filePreview.src} 
              alt="Uploaded content" 
              className="file-preview" 
            />
          ) : (
            <video 
              src={filePreview.src} 
              controls 
              className="file-preview"
            />
          )}
        </Box>
      )}

      {/* Analysis Summary Card */}
      <Card 
        elevation={3} 
        sx={{ 
          mb: 3, 
          borderRadius: 2,
          borderLeft: 5,
          borderColor: statusColor
        }}
      >
        <CardContent sx={{ display: 'flex', alignItems: 'center' }}>
          <Box sx={{ mr: 2 }}>
            {statusIcon}
          </Box>
          <Box>
            <Typography variant="h6" component="div">
              {likelihood === 'High' 
                ? 'Likely AI-Generated Content' 
                : likelihood === 'Low' 
                  ? 'Likely Authentic Content' 
                  : 'Analysis Inconclusive'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {maliciousIntent === 'Yes' 
                ? 'Potential malicious intent detected' 
                : maliciousIntent === 'No' 
                  ? 'No malicious intent detected' 
                  : 'Malicious intent assessment inconclusive'}
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Confidence Chart */}
      <ConfidenceChart probability={probability} isFake={isFake} />

      {/* Structured Analysis Section */}
      {structuredAnalysisMatch && (
        <Paper elevation={2} sx={{ p: 3, mb: 3, borderRadius: 2 }}>
          <Typography variant="h5" gutterBottom>
            Detailed Analysis
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Box className="analysis-container">
            {structuredAnalysisMatch[1].split(/\d+\./).map((section, index) => {
              if (index === 0) return null; // Skip the first empty split
              
              // Extract the section title and content
              const lines = section.trim().split('\n');
              const title = lines[0].trim();
              const content = lines.slice(1).join('\n').trim();
              
              return (
                <Box key={index} className="analysis-section">
                  <Typography variant="h6">{index}. {title}</Typography>
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
                    {content}
                  </Typography>
                </Box>
              );
            })}
          </Box>
        </Paper>
      )}

      {/* Assessment Section */}
      {assessmentMatch && (
        <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
          <Typography variant="h5" gutterBottom>
            Assessment
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Box className="analysis-container">
            <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
              {assessmentMatch[1]}
            </Typography>
          </Box>
        </Paper>
      )}

      {/* If no structured format is found, display the raw result */}
      {!structuredAnalysisMatch && !assessmentMatch && (
        <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
          <Typography variant="h5" gutterBottom>
            Analysis Result
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
            {result}
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default AnalysisResult; 