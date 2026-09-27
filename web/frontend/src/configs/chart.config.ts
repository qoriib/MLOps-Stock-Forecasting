import type { EChartsOption } from 'echarts'
import { formatCurrency } from '@/utils'

/**
 * Reads a CSS custom property by locating the Astryx theme element in the DOM.
 * Astryx scopes design tokens to [data-astryx-theme], not :root.
 */
function cssVar(name: string): string {
  const el = document.querySelector('[data-astryx-theme]') ?? document.documentElement
  return getComputedStyle(el).getPropertyValue(name).trim()
}

/**
 * Generates base ECharts configuration using Astryx CSS design tokens.
 * Colors adapt automatically to light/dark theme changes.
 */
export function getEChartsThemeOptions(): Partial<EChartsOption> {
  const textPrimary = cssVar('--color-text-primary')
  const textSecondary = cssVar('--color-text-secondary')
  const bgPopover = cssVar('--color-background-popover')
  const borderColor = cssVar('--color-border')
  const fontBody = cssVar('--font-family-body')
  const fontMono = cssVar('--font-family-code')

  return {
    textStyle: {
      fontFamily: fontBody,
      color: textPrimary,
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross', crossStyle: { color: textSecondary } },
      backgroundColor: bgPopover,
      borderColor: borderColor,
      borderWidth: 1,
      textStyle: { color: textPrimary, fontFamily: fontBody, fontSize: 12 },
      padding: [10, 14],
    },
    grid: {
      left: '3%',
      right: '4%',
      top: '12%',
      bottom: '14%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: true,
      axisLine: { onZero: false, lineStyle: { color: borderColor } },
      axisTick: { lineStyle: { color: borderColor } },
      splitLine: { show: false },
      axisLabel: { color: textSecondary, fontFamily: fontBody, fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      scale: true,
      splitLine: { show: true, lineStyle: { color: borderColor, type: 'dashed' } },
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: textSecondary,
        fontFamily: fontMono,
        fontSize: 11,
        formatter: (value: number) => formatCurrency(value),
      },
    },
    dataZoom: [
      { type: 'inside', start: 0, end: 100 },
      {
        type: 'slider',
        show: true,
        bottom: '2%',
        height: 20,
        borderColor: 'transparent',
        backgroundColor: 'transparent',
        fillerColor: cssVar('--color-accent-muted'),
        handleStyle: { color: cssVar('--color-accent'), borderColor: bgPopover },
        textStyle: { color: textSecondary, fontSize: 10, fontFamily: fontMono },
      },
    ],
  }
}
