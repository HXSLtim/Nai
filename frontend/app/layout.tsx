'use client';

import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { createAppTheme } from '@/theme/theme';
import { useState, useMemo } from 'react';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [mode, setMode] = useState<'light' | 'dark'>('light');
  const theme = useMemo(() => createAppTheme(mode), [mode]);

  return (
    <html lang="zh-CN">
      <body>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
