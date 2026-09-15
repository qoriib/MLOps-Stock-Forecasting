import { Card, Text, Timestamp } from '@astryxdesign/core'
import { Layout, LayoutContent } from '@astryxdesign/core/Layout'
import { Table, pixel, proportional } from '@astryxdesign/core/Table'
import { useStockStore } from '@/stores'
import { formatCurrency } from '@/utils'
import type { TableColumn } from '@astryxdesign/core/Table'
import type { PredictionItem } from '@/types'

const COLUMNS: TableColumn<PredictionItem>[] = [
  {
    key: 'date',
    header: 'Tanggal',
    width: proportional(1),
    renderCell: (row) => (
      <Timestamp value={row.date} format="date" type="body" weight="medium" />
    ),
  },
  {
    key: 'predicted',
    header: 'Prediksi',
    width: pixel(180),
    renderCell: (row) => (
      <Text type="code" weight="semibold" hasTabularNumbers>
        {formatCurrency(row.predicted_price, { minimumFractionDigits: 2 })}
      </Text>
    ),
  },
  {
    key: 'lower_bound',
    header: 'Batas Bawah',
    width: pixel(180),
    renderCell: (row) => (
      <Text type="code" color="secondary" hasTabularNumbers>
        {formatCurrency(row.lower_bound, { minimumFractionDigits: 2 })}
      </Text>
    ),
  },
  {
    key: 'upper_bound',
    header: 'Batas Atas',
    width: pixel(180),
    renderCell: (row) => (
      <Text type="code" color="secondary" hasTabularNumbers>
        {formatCurrency(row.upper_bound, { minimumFractionDigits: 2 })}
      </Text>
    ),
  },
]

export function ForecastTable() {
  const items = useStockStore((state) => state.predictResult?.predictions)

  if (!items || items.length === 0) return null

  return (
    <Card variant="default">
      <Layout
        content={
          <LayoutContent padding={0}>
            <Table
              data={items}
              columns={COLUMNS}
              idKey="date"
              hasHover
            />
          </LayoutContent>
        }
      />
    </Card>
  )
}
