'use client';

import * as React from 'react';
import { CacheProvider } from '@emotion/react';
import createCache from '@emotion/cache';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';

const muiTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2'
    },
    warning: {
      main: '#ffb300'
    },
    error: {
      main: '#d32f2f'
    },
    success: {
      main: '#2e7d32'
    }
  },
  typography: {
    fontFamily: 'Roboto, sans-serif'
  }
});

const cache = createCache({ key: 'mui', prepend: true });

export default function ThemeRegistry({ children }: { children: React.ReactNode }) {
  return (
    <CacheProvider value={cache}>
      <ThemeProvider theme={muiTheme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </CacheProvider>
  );
}
