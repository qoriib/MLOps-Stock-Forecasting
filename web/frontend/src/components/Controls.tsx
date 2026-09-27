import { useEffect } from 'react'
import { useForm } from '@tanstack/react-form'
import {
  Button,
  Card,
  Center,
  DateRangeInput,
  FormLayout,
  HStack,
  Selector,
  Spinner,
} from '@astryxdesign/core'
import type { DateRange } from '@astryxdesign/core/DateRangeInput'
import { useStockStore, useShallow } from '@/stores'
import { HISTORY_RANGE_PRESETS, FORECAST_RANGE_PRESETS } from '@/configs'

interface ForecastFormValues {
  ticker: string
  model: string
  historyRange: DateRange | null
  forecastRange: DateRange | null
}

export function Controls() {
  const {
    ticker,
    model,
    availableTickers,
    availableModels,
    loadingOptions,
    historyRange,
    forecastRange,
    loading,
    setTicker,
    setModel,
    setHistoryRange,
    setForecastRange,
    runAnalysis,
  } = useStockStore(
    useShallow((state) => ({
      ticker: state.ticker,
      model: state.model,
      availableTickers: state.availableTickers,
      availableModels: state.availableModels,
      loadingOptions: state.loadingOptions,
      historyRange: state.historyRange,
      forecastRange: state.forecastRange,
      loading: state.loading,
      setTicker: state.setTicker,
      setModel: state.setModel,
      setHistoryRange: state.setHistoryRange,
      setForecastRange: state.setForecastRange,
      runAnalysis: state.runAnalysis,
    })),
  )

  const form = useForm({
    defaultValues: { ticker, model, historyRange, forecastRange } as ForecastFormValues,
    onSubmit: async ({ value }) => {
      if (!value.ticker || !value.historyRange?.start || !value.forecastRange?.start) return

      setTicker(value.ticker)
      setModel(value.model)
      setHistoryRange(value.historyRange)
      setForecastRange(value.forecastRange)

      runAnalysis({
        ticker: value.ticker,
        model: value.model,
        historyRange: value.historyRange,
        forecastRange: value.forecastRange,
      })
    },
  })

  // Sync form when store values update (e.g. after initial API fetch)
  useEffect(() => {
    if (ticker) form.setFieldValue('ticker', ticker)
  }, [ticker, form])

  useEffect(() => {
    if (model) form.setFieldValue('model', model)
  }, [model, form])

  useEffect(() => {
    if (historyRange) form.setFieldValue('historyRange', historyRange)
  }, [historyRange, form])

  useEffect(() => {
    if (forecastRange) form.setFieldValue('forecastRange', forecastRange)
  }, [forecastRange, form])

  const tickerOptions = availableTickers.map((t) => ({ value: t, label: t }))
  const modelOptions = availableModels.map((m) => ({ value: m, label: m.toUpperCase() }))

  if (loadingOptions) {
    return (
      <Card variant="default" padding={4}>
        <Center height={48}>
          <Spinner label="Loading options..." />
        </Center>
      </Card>
    )
  }

  return (
    <Card variant="default" padding={4}>
      <form
        onSubmit={(e) => {
          e.preventDefault()
          e.stopPropagation()
          form.handleSubmit()
        }}
      >
        <HStack align="end" wrap="wrap" gap={3}>
          <FormLayout direction="horizontal" style={{ flex: 1, minWidth: 0 }}>
            <form.Field
              name="ticker"
              validators={{ onChange: ({ value }) => (!value ? 'Stock ticker is required' : undefined) }}
            >
              {(field) => {
                const error = field.state.meta.errors[0]
                return (
                  <Selector
                    label="Stock Ticker"
                    placeholder="Select Ticker"
                    options={tickerOptions}
                    value={field.state.value}
                    onChange={(value) => field.handleChange(value as string)}
                    isDisabled={loading || tickerOptions.length === 0}
                    status={error ? { type: 'error', message: String(error) } : undefined}
                  />
                )
              }}
            </form.Field>

            <form.Field
              name="model"
              validators={{ onChange: ({ value }) => (!value ? 'Prediction model is required' : undefined) }}
            >
              {(field) => {
                const error = field.state.meta.errors[0]
                return (
                  <Selector
                    label="Model"
                    placeholder="Select Model"
                    options={modelOptions}
                    value={field.state.value}
                    onChange={(value) => field.handleChange(value as string)}
                    isDisabled={loading || modelOptions.length === 0}
                    status={error ? { type: 'error', message: String(error) } : undefined}
                  />
                )
              }}
            </form.Field>

            <form.Field
              name="historyRange"
              validators={{
                onChange: ({ value }) =>
                  !value?.start || !value?.end ? 'Historical range is required' : undefined,
              }}
            >
              {(field) => {
                const error = field.state.meta.errors[0]
                return (
                  <DateRangeInput
                    label="Historical Data (OHLC)"
                    placeholder="Select historical range"
                    value={field.state.value}
                    onChange={(value) => field.handleChange(value)}
                    presets={HISTORY_RANGE_PRESETS}
                    isDisabled={loading}
                    status={error ? { type: 'error', message: String(error) } : undefined}
                  />
                )
              }}
            </form.Field>

            <form.Field
              name="forecastRange"
              validators={{
                onChange: ({ value }) =>
                  !value?.start || !value?.end ? 'Forecast range is required' : undefined,
              }}
            >
              {(field) => {
                const error = field.state.meta.errors[0]
                return (
                  <DateRangeInput
                    label="Forecast Range"
                    placeholder="Select forecast range"
                    value={field.state.value}
                    onChange={(value) => field.handleChange(value)}
                    presets={FORECAST_RANGE_PRESETS}
                    isDisabled={loading}
                    status={error ? { type: 'error', message: String(error) } : undefined}
                  />
                )
              }}
            </form.Field>
          </FormLayout>

          <form.Subscribe selector={(state) => [state.canSubmit, state.isSubmitting]}>
            {([canSubmit, isSubmitting]) => (
              <Button
                variant="primary"
                label={loading || isSubmitting ? 'Processing...' : 'Run Analysis'}
                isLoading={loading || isSubmitting}
                isDisabled={loading || isSubmitting || !canSubmit}
                onClick={() => form.handleSubmit()}
              />
            )}
          </form.Subscribe>
        </HStack>
      </form>
    </Card>
  )
}
