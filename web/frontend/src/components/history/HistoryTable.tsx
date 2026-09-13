import { Card } from '@astryxdesign/core/Card'
import { Text } from '@astryxdesign/core/Text'
import { Table, proportional, pixel } from '@astryxdesign/core/Table'
import type { TableColumn } from '@astryxdesign/core/Table'
import type { HistoricalItem } from '@/types/stock'

interface HistoryTableProps {
  items: HistoricalItem[]
}

const COLUMNS: TableColumn<HistoricalItem>[] = [
  {
    key: 'date',
    header: 'Tanggal Transaksi',
    width: proportional(1),
    renderCell: (row) => <Text weight="medium">{String(row.date)}</Text>,
  },
  {
    key: 'open',
    header: 'Harga Pembukaan',
    width: proportional(1),
    renderCell: (row) => `Rp ${Number(row.open).toLocaleString('id-ID')}`,
  },
  {
    key: 'high',
    header: 'Tertinggi (High)',
    width: proportional(1),
    renderCell: (row) => `Rp ${Number(row.high).toLocaleString('id-ID')}`,
  },
  {
    key: 'low',
    header: 'Terendah (Low)',
    width: proportional(1),
    renderCell: (row) => `Rp ${Number(row.low).toLocaleString('id-ID')}`,
  },
  {
    key: 'close',
    header: 'Harga Penutupan',
    width: proportional(1),
    renderCell: (row) => (
      <Text weight="semibold">Rp {Number(row.close).toLocaleString('id-ID')}</Text>
    ),
  },
  {
    key: 'volume',
    header: 'Volume Perdagangan',
    width: pixel(180),
    renderCell: (row) => Number(row.volume).toLocaleString('id-ID'),
  },
]

export function HistoryTable({ items }: HistoryTableProps) {
  return (
    <Card>
      <Table
        hasHover
        idKey="date"
        data={items}
        columns={COLUMNS}
      />
    </Card>
  )
}
