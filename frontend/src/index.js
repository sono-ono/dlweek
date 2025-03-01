import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Create a holographic theme with red accents
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#e91e63', // Pink-red as primary color
      light: '#ff6090',
      dark: '#b0003a',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#00bcd4', // Cyan as secondary color
      light: '#62efff',
      dark: '#008ba3',
      contrastText: '#000000',
    },
    error: {
      main: '#f44336', // Red for error/warning
    },
    success: {
      main: '#00e676', // Bright green for success
    },
    background: {
      default: '#f5f5f7', // Light gray with slight blue tint
      paper: '#ffffff',
    },
    holographic: {
      gradient: 'linear-gradient(135deg, #ff6090 0%, #00bcd4 50%, #e91e63 100%)',
      shimmer: 'linear-gradient(45deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.8) 50%, rgba(255,255,255,0) 100%)',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 500,
    },
    h2: {
      fontWeight: 500,
    },
    h3: {
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 12, // Increased border radius for a more modern look
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 12,
          padding: '10px 20px',
          boxShadow: '0 4px 20px 0 rgba(233, 30, 99, 0.2)',
        },
        contained: {
          background: 'linear-gradient(45deg, #e91e63 30%, #ff6090 90%)',
          '&:hover': {
            background: 'linear-gradient(45deg, #b0003a 30%, #e91e63 90%)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 4px 20px 0 rgba(0,0,0,0.1)',
          position: 'relative',
          overflow: 'hidden',
          '&::after': {
            content: '""',
            position: 'absolute',
            top: '-50%',
            left: '-50%',
            width: '200%',
            height: '200%',
            background: 'linear-gradient(45deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0) 100%)',
            transform: 'rotate(30deg)',
            animation: 'shimmer 3s infinite',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.95) 100%)',
          backdropFilter: 'blur(10px)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(90deg, #b0003a 0%, #e91e63 50%, #ff6090 100%)',
          boxShadow: '0 4px 20px 0 rgba(233, 30, 99, 0.3)',
        },
      },
    },
  },
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);

reportWebVitals(); 