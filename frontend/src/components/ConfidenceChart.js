import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { Box, Typography, Paper, Grid } from '@mui/material';
import VerifiedIcon from '@mui/icons-material/Verified';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';

const ConfidenceChart = ({ probability, isFake }) => {
  // Convert probability to percentage
  const confidencePercentage = Math.round(probability * 100);
  
  // Create data for the pie chart - the first value should always be the confidence in the result
  // (whether it's confidence in being fake or confidence in being real)
  const data = [
    { 
      name: isFake ? 'AI-Generated' : 'Authentic', 
      value: confidencePercentage 
    },
    { 
      name: 'Uncertainty', 
      value: 100 - confidencePercentage 
    }
  ];

  // Define colors based on whether the content is detected as fake or real
  // Using a more holographic red-themed color palette
  const COLORS = isFake 
    ? ['#ff1744', '#b71c1c'] // Bright red and dark red for fake
    : ['#00e676', '#00c853']; // Keep green for real but adjust shades

  // Define the confidence level text
  let confidenceLevelText = 'Moderate';
  if (confidencePercentage >= 90) {
    confidenceLevelText = 'Very High';
  } else if (confidencePercentage >= 75) {
    confidenceLevelText = 'High';
  } else if (confidencePercentage >= 60) {
    confidenceLevelText = 'Moderate';
  } else if (confidencePercentage >= 40) {
    confidenceLevelText = 'Low';
  } else {
    confidenceLevelText = 'Very Low';
  }

  // Custom tooltip for the pie chart
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip" style={{ 
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          padding: '10px',
          border: '1px solid #e91e63',
          borderRadius: '8px',
          boxShadow: '0 4px 20px rgba(233, 30, 99, 0.3)'
        }}>
          <p style={{ color: payload[0].color, margin: '0', fontWeight: 'bold' }}>
            {`${payload[0].name}: ${payload[0].value}%`}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <Paper 
      elevation={3} 
      sx={{ 
        p: 3, 
        borderRadius: 3, 
        mb: 3,
        background: 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.8) 100%)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(233, 30, 99, 0.2)',
        boxShadow: '0 10px 30px rgba(233, 30, 99, 0.15)',
        position: 'relative',
        overflow: 'hidden',
        '&::after': {
          content: '""',
          position: 'absolute',
          top: '-100%',
          left: '-100%',
          width: '300%',
          height: '300%',
          background: 'linear-gradient(45deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.3) 50%, rgba(255,255,255,0) 100%)',
          transform: 'rotate(30deg)',
          animation: 'shimmer 6s infinite linear',
          zIndex: 1,
          pointerEvents: 'none',
        }
      }}
      className="holographic-card"
    >
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} md={6}>
          <Box sx={{ 
            textAlign: 'center', 
            mb: { xs: 2, md: 0 },
            position: 'relative',
            zIndex: 2
          }}>
            <Typography 
              variant="h6" 
              gutterBottom 
              sx={{ 
                fontWeight: 'bold',
                background: isFake 
                  ? 'linear-gradient(45deg, #ff1744 30%, #f50057 90%)' 
                  : 'linear-gradient(45deg, #00e676 30%, #00c853 90%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                textShadow: '0 2px 10px rgba(233, 30, 99, 0.2)'
              }}
            >
              Confidence Level: {confidenceLevelText}
            </Typography>
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              mb: 1,
              background: 'rgba(255, 255, 255, 0.7)',
              borderRadius: '50px',
              padding: '8px 16px',
              boxShadow: '0 4px 20px rgba(233, 30, 99, 0.15)',
              border: '1px solid rgba(233, 30, 99, 0.1)',
            }}>
              {isFake ? (
                <WarningAmberIcon sx={{ 
                  color: '#ff1744', 
                  mr: 1, 
                  fontSize: 32,
                  filter: 'drop-shadow(0 0 5px rgba(255, 23, 68, 0.5))'
                }} />
              ) : (
                <VerifiedIcon sx={{ 
                  color: '#00e676', 
                  mr: 1, 
                  fontSize: 32,
                  filter: 'drop-shadow(0 0 5px rgba(0, 230, 118, 0.5))'
                }} />
              )}
              <Typography 
                variant="h3" 
                component="span" 
                sx={{ 
                  fontWeight: 'bold',
                  color: isFake ? '#ff1744' : '#00e676',
                  textShadow: isFake 
                    ? '0 0 10px rgba(255, 23, 68, 0.3)' 
                    : '0 0 10px rgba(0, 230, 118, 0.3)'
                }}
              >
                {confidencePercentage}%
              </Typography>
            </Box>
            <Typography 
              variant="body1" 
              sx={{ 
                fontWeight: 'medium',
                color: isFake ? '#d32f2f' : '#2e7d32'
              }}
            >
              {isFake 
                ? 'Likelihood of being AI-generated' 
                : 'Likelihood of being authentic'}
            </Typography>
            <Typography 
              variant="body2" 
              color="text.secondary" 
              sx={{ 
                mt: 1,
                fontStyle: 'italic',
                background: 'rgba(255, 255, 255, 0.7)',
                padding: '4px 12px',
                borderRadius: '16px',
                display: 'inline-block'
              }}
            >
              Based on deepfake detection analysis
            </Typography>
          </Box>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Box 
            sx={{ 
              height: 220, 
              width: '100%',
              position: 'relative',
              zIndex: 2
            }}
            className="confidence-chart-container"
          >
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  fill="#8884d8"
                  paddingAngle={5}
                  dataKey="value"
                  strokeWidth={3}
                  stroke="rgba(255, 255, 255, 0.8)"
                >
                  {data.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={index === 0 ? COLORS[0] : '#e0e0e0'} 
                      style={{
                        filter: index === 0 ? `drop-shadow(0 0 8px ${COLORS[1]})` : 'none'
                      }}
                    />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend 
                  verticalAlign="bottom" 
                  height={36} 
                  formatter={(value, entry, index) => (
                    <span style={{ 
                      color: index === 0 ? COLORS[0] : '#757575',
                      fontWeight: index === 0 ? 'bold' : 'normal'
                    }}>
                      {value}
                    </span>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default ConfidenceChart; 