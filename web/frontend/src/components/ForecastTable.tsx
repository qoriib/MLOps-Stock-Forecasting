import { useMemo } from 'react'
import {
  Card,
  HStack,
  pixel,
  Table,
  Text,
  Timestamp,
  Token,
  useTableStickyColumns,
  type TableColumn,
} from '@astryxdesign/core'
import { Layout, LayoutContent } from '@astryxdesign/core/Layout'
import { useStockStore, useShallow } from '@/stores'
import { formatCurrency } from '@/utils'

interface ForecastTableRow extends Record<string, unknown> {
  id: string
  date: string
  price: number
  formattedPrice: string
  dailyDiff: number
  dailyPct: number
  cumulativeDiff: number
  cumulativePct: number
}

export function ForecastTable() {
  const { historyData, forecastData } = useStockStore(
    useShallow((state) => ({
      historyData: state.historyData,
      forecastData: state.forecastData,
    })),
  )

  const baselineLastClose = useMemo(() => {
    if (historyData.length === 0) {
      return 0
    }
    return historyData[historyData.length - 1].close
  }, [historyData])

  const tableData: ForecastTableRow[] = useMemo(() => {
    if (!forecastData || forecastData.length === 0) {
      return []
    }

    let previousPrice = baselineLastClose

    return forecastData.map((forecastPoint) => {
      const currentPrice = forecastPoint.predicted_price
      const dailyDiff = previousPrice > 0 ? currentPrice - previousPrice : 0
      const dailyPct = previousPrice > 0 ? (dailyDiff / previousPrice) * 100 : 0

      const cumulativeDiff = baselineLastClose > 0 ? currentPrice - baselineLastClose : 0
      const cumulativePct = baselineLastClose > 0 ? (cumulativeDiff / baselineLastClose) * 100 : 0

      // Update previous price untuk baris berikutnya
      previousPrice = currentPrice

      return {
        id: forecastPoint.date,
        date: forecastPoint.date,
        price: currentPrice,
        formattedPrice: formatCurrency(currentPrice),
        dailyDiff,
        dailyPct,
        cumulativeDiff,
        cumulativePct,
      }
    })
  }, [forecastData, baselineLastClose])

  const stickyColumnsPlugin = useTableStickyColumns<ForecastTableRow>({
    startKeys: ['date'],
  })

  const columns: TableColumn<ForecastTableRow>[] = useMemo(
    () => [
      {
        key: 'date',
        header: 'Forecast Date',
        align: 'start',
        width: pixel(190),
        renderCell: (row) => (
          <Timestamp
            value={row.date}
            format="date"
            size="base"
          />
        ),
      },
      {
        key: 'formattedPrice',
        header: 'Predicted Price',
        align: 'end',
        width: pixel(220),
        renderCell: (row) => (
          <Text type="code" hasTabularNumbers textWrap="nowrap" weight="bold">
            {row.formattedPrice}
          </Text>
        ),
      },
      {
        key: 'dailyChange',
        header: 'Daily Change (DoD)',
        align: 'end',
        width: pixel(280),
        renderCell: (row) => {
          const isPositive = row.dailyDiff > 0
          const isNegative = row.dailyDiff < 0
          const sign = isPositive ? '+' : ''
          const tokenColor = isPositive ? 'green' : isNegative ? 'red' : 'gray'

          return (
            <HStack justify="end" align="center" wrap="nowrap" gap={2}>
              <Text type="code" hasTabularNumbers textWrap="nowrap" weight="medium">
                {sign}{formatCurrency(row.dailyDiff)}
              </Text>
              <Token
                color={tokenColor}
                label={`${sign}${row.dailyPct.toFixed(2)}%`}
              />
            </HStack>
          )
        },
      },
      {
        key: 'cumulativeChange',
        header: 'Cumulative Change',
        align: 'end',
        width: pixel(300),
        renderCell: (row) => {
          const isPositive = row.cumulativeDiff > 0
          const isNegative = row.cumulativeDiff < 0
          const sign = isPositive ? '+' : ''
          const tokenColor = isPositive ? 'green' : isNegative ? 'red' : 'gray'

          return (
            <HStack justify="end" align="center" wrap="nowrap" gap={2}>
              <Text type="code" hasTabularNumbers textWrap="nowrap" weight="medium">
                {sign}{formatCurrency(row.cumulativeDiff)}
              </Text>
              <Token
                color={tokenColor}
                label={`${sign}${row.cumulativePct.toFixed(2)}%`}
              />
            </HStack>
          )
        },
      },
    ],
    [],
  )

  if (!forecastData || forecastData.length === 0) {
    return null
  }

  return (
    <Card variant="default">
      <Layout
        content={
          <LayoutContent>
            <Table<ForecastTableRow>
              data={tableData}
              columns={columns}
              plugins={{ stickyColumns: stickyColumnsPlugin }}
              dividers="rows"
              hasHover
            />
          </LayoutContent>
        }
      />
    </Card>
  )
}
