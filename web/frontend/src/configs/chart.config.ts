import type { EChartsOption } from 'echarts'
import { formatCurrency } from '@/utils'

export const BODY_FONT_FAMILY =
  'Figtree, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'

export const MONO_FONT_FAMILY =
  'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace'

/**
 * Menghasilkan konfigurasi dasar ECharts yang beradaptasi secara dinamis
 * dengan token tema Astryx (Mode Dark / Light).
 */
export function getEChartsThemeOptions(isDark: boolean = true): Partial<EChartsOption> {
  const textPrimary = isDark ? '#f3f4f6' : '#111827'
  const textMuted = isDark ? '#9ca3af' : '#6b7280'
  const borderColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)'
  const splitLineColor = isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'
  const tooltipBg = isDark ? 'rgba(24, 24, 27, 0.95)' : 'rgba(255, 255, 255, 0.95)'
  const tooltipBorder = isDark ? '#27272a' : '#e5e7eb'

  return {
    textStyle: {
      fontFamily: BODY_FONT_FAMILY,
      color: textPrimary,
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        crossStyle: {
          color: textMuted,
        },
      },
      backgroundColor: tooltipBg,
      borderColor: tooltipBorder,
      borderWidth: 1,
      textStyle: {
        color: textPrimary,
        fontFamily: BODY_FONT_FAMILY,
        fontSize: 12,
      },
      padding: [10, 14],
    },
    grid: {
      left: '3%',
      right: '4%',
      top: '12%',
      bottom: '14%',
      containLabel: true,
      borderColor: borderColor,
    },
    xAxis: {
      type: 'category',
      boundaryGap: true,
      axisLine: {
        onZero: false,
        lineStyle: { color: borderColor },
      },
      axisTick: { lineStyle: { color: borderColor } },
      splitLine: { show: false },
      axisLabel: {
        color: textMuted,
        fontFamily: BODY_FONT_FAMILY,
        fontSize: 11,
      },
    },
    yAxis: {
      type: 'value',
      scale: true,
      splitLine: {
        show: true,
        lineStyle: {
          color: splitLineColor,
          type: 'dashed',
        },
      },
      axisLine: {
        show: false,
      },
      axisTick: { show: false },
      axisLabel: {
        color: textMuted,
        fontFamily: MONO_FONT_FAMILY,
        fontSize: 11,
        formatter: (val: number) => formatCurrency(val),
      },
    },
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100,
      },
      {
        type: 'slider',
        show: true,
        bottom: '2%',
        height: 20,
        borderColor: 'transparent',
        backgroundColor: isDark ? 'rgba(255, 255, 255, 0.03)' : 'rgba(0, 0, 0, 0.03)',
        fillerColor: isDark ? 'rgba(99, 102, 241, 0.2)' : 'rgba(99, 102, 241, 0.15)',
        handleStyle: {
          color: '#6366f1',
          borderColor: isDark ? '#1e1e24' : '#ffffff',
        },
        textStyle: {
          color: textMuted,
          fontSize: 10,
        },
      },
    ],
  }
}
