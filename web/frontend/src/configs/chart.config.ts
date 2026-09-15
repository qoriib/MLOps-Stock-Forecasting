import type { ApexOptions } from 'apexcharts'
import { formatCurrency } from '@/utils'

export const MONO_FONT_FAMILY =
  'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace'

export function getApexThemeOptions(isDark: boolean = true): ApexOptions {
  const textMuted = isDark ? '#9ca3af' : '#6b7280'
  const gridBorder = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)'
  const axisBorder = isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)'
  const crosshairBorder = isDark ? 'rgba(255, 255, 255, 0.25)' : 'rgba(0, 0, 0, 0.2)'
  const bodyFont = 'Figtree, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'

  return {
    theme: {
      mode: isDark ? 'dark' : 'light',
    },
    chart: {
      background: 'transparent',
      foreColor: textMuted,
      fontFamily: bodyFont,
      toolbar: { show: false },
      zoom: { enabled: false },
    },
    grid: {
      borderColor: gridBorder,
      strokeDashArray: 3,
      xaxis: { lines: { show: false } },
      yaxis: { lines: { show: true } },
    },
    tooltip: {
      theme: isDark ? 'dark' : 'light',
      style: {
        fontSize: '12px',
        fontFamily: bodyFont,
      },
      x: { format: 'dd MMM yyyy' },
      y: {
        formatter: (val) => formatCurrency(val),
      },
    },
    xaxis: {
      type: 'datetime',
      axisBorder: { color: axisBorder },
      axisTicks: { color: axisBorder },
      crosshairs: {
        show: true,
        stroke: {
          color: crosshairBorder,
          width: 1,
          dashArray: 3,
        },
      },
      labels: {
        format: 'dd MMM yyyy',
        style: {
          colors: textMuted,
          fontFamily: bodyFont,
          fontSize: '11px',
        },
      },
    },
    yaxis: {
      crosshairs: {
        show: true,
        stroke: {
          color: crosshairBorder,
          width: 1,
          dashArray: 3,
        },
      },
      labels: {
        style: {
          colors: textMuted,
          fontFamily: MONO_FONT_FAMILY,
          fontSize: '11px',
        },
        formatter: (val) => formatCurrency(val),
      },
    },
    legend: {
      labels: {
        colors: textMuted,
      },
    },
  }
}
