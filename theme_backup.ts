'use client';

import { createTheme, PaletteMode } from '@mui/material/styles';

/**
 * 纸墨配色方案 - 浅色模式
 */
const lightPalette = {
  primary: {
    main: '#006C52',        // 低饱和绿
    contrastText: '#FFFFFF',
    container: '#D4F5E9',
  },
  secondary: {
    main: '#5F5F5F',        // 灰
    contrastText: '#FFFFFF',
  },
  background: {
    default: '#F9F7F2',     // 纸白
    paper: '#FFFFFF',
  },
  text: {
    primary: '#1D1C1A',     // 墨黑 (87% opacity)
    secondary: '#5F5F5F',
  },
  divider: '#C7C2B9',
  mode: 'light' as PaletteMode,
};

/**
 * 纸墨配色方案 - 深色模式
 */
const darkPalette = {
  primary: {
    main: '#4EC9A1',        // 降低亮度的绿
    contrastText: '#000000',
    container: '#004D3A',
  },
  secondary: {
    main: '#9E9E9E',
    contrastText: '#000000',
  },
  background: {
    default: '#1B1B1B',     // 纯黑5%上浮
    paper: '#242424',
  },
  text: {
    primary: '#E2E0DB',     // 米白 (93% white)
    secondary: '#9E9E9E',
  },
  divider: '#494944',
  mode: 'dark' as PaletteMode,
};

/**
 * 创建应用主题
 * @param mode - 主题模式（light/dark）
 */
export const createAppTheme = (mode: PaletteMode) => {
  const palette = mode === 'light' ? lightPalette : darkPalette;

  return createTheme({
    palette,
    typography: {
      fontFamily: [
        '-apple-system',
        'BlinkMacSystemFont',
        '"Segoe UI"',
        'Roboto',
        '"Noto Sans SC"',
        'sans-serif',
      ].join(','),
      // 针对阅读优化的字体大小
      body1: {
        fontSize: '16px',
        lineHeight: 1.75,
        letterSpacing: '0.02em',
      },
      h1: {
        fontSize: '2.5rem',
        fontWeight: 600,
      },
      h2: {
        fontSize: '2rem',
        fontWeight: 600,
      },
    },
    shape: {
      borderRadius: 8,
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            borderRadius: '8px',
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            boxShadow: mode === 'light'
              ? '0 2px 8px rgba(0,0,0,0.08)'
              : '0 2px 8px rgba(0,0,0,0.3)',
          },
        },
      },
    },
  });
};
