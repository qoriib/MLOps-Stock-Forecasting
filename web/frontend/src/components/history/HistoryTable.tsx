import { Card, Text, Timestamp } from '@astryxdesign/core'
import { Layout, LayoutContent } from '@astryxdesign/core/Layout'
import { Table, proportional, pixel } from '@astryxdesign/core/Table'
import { formatCurrency, formatNumber } from '@/utils'
import { useStockStore, selectFilteredHistory } from '@/stores'
import type { TableColumn } from '@astryxdesign/core/Table'
import type { HistoricalItem } from '@/types'

const COLUMNS: TableColumn<HistoricalItem>[] = [
  {
    key: 'date',
    header: 'Tanggal',
    width: proportional(1),
    renderCell: (row) => (
      <Timestamp value={row.date} format="date" type="body" weight="medium" />
    ),
  },
  {
    key: 'open',
    header: 'Pembukaan',
    width: pixel(180),
    renderCell: (row) => (
      <Text type="code" hasTabularNumbers>
        {formatCurrency(row.open)}
      </Text>
    ),
  },
  {
    key: 'high',
    header: 'Tertinggi',
    width: pixel(180),
    renderCell: (row) => (
      <Text type="code" hasTabularNumbers>
        {formatCurrency(row.high)}
      </Text>
    ),
  },
  {
    key: 'low',
    header: 'Terendah',
    width: pixel(180),
    renderCell: (row) => (
      <Text type="code" hasTabularNumbers>
        {formatCurrency(row.low)}
      </Text>
    ),
  },
  {
    key: 'close',
    header: 'Penutupan',
    width: pixel(180),
    renderCell: (row) => (
      <Text type="code" weight="semibold" hasTabularNumbers>
        {formatCurrency(row.close)}
      </Text>
    ),
  },
  {
    key: 'volume',
    header: 'Volume',
    width: pixel(180),
    renderCell: (row) => (
      <Text type="code" hasTabularNumbers>
        {formatNumber(row.volume)}
      </Text>
    ),
  },
]

export function HistoryTable() {
  const items = useStockStore(selectFilteredHistory)

  return (
    <Card variant="default">
      <Layout
        content={
          <LayoutContent padding={0}>
            <Table
              hasHover
              idKey="date"
              data={items}
              columns={COLUMNS}
            />
          </LayoutContent>
        }
      />
    </Card>
  )
}

