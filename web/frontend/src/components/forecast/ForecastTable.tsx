import { Card } from '@astryxdesign/core/Card'
import { Text } from '@astryxdesign/core/Text'
import { Table, proportional } from '@astryxdesign/core/Table'
import type { TableColumn } from '@astryxdesign/core/Table'
import type { PredictionItem } from '@/types/stock'

interface ForecastTableProps {
  items: PredictionItem[]
}

const COLUMNS: TableColumn<PredictionItem>[] = [
  {
    key: 'date',
    header: 'Tanggal Bursa',
    width: proportional(1),
    renderCell: (row) => <Text weight="medium">{String(row.date)}</Text>,
  },
  {
    key: 'predicted_price',
    header: 'Prediksi Harga',
    width: proportional(1),
    renderCell: (row) => (
      <Text weight="semibold">
        Rp {Number(row.predicted_price).toLocaleString('id-ID', { minimumFractionDigits: 2 })}
      </Text>
    ),
  },
  {
    key: 'lower_bound',
    header: 'Batas Bawah (95% CI)',
    width: proportional(1),
    renderCell: (row) => (
      <Text color="secondary">
        {row.lower_bound != null
          ? `Rp ${Number(row.lower_bound).toLocaleString('id-ID', { minimumFractionDigits: 2 })}`
          : '—'}
      </Text>
    ),
  },
  {
    key: 'upper_bound',
    header: 'Batas Atas (95% CI)',
    width: proportional(1),
    renderCell: (row) => (
      <Text color="secondary">
        {row.upper_bound != null
          ? `Rp ${Number(row.upper_bound).toLocaleString('id-ID', { minimumFractionDigits: 2 })}`
          : '—'}
      </Text>
    ),
  },
]

export function ForecastTable({ items }: ForecastTableProps) {
  return (
    <Card variant="default" padding={0}>
      <Table
        data={items}
        columns={COLUMNS}
        idKey="date"
        hasHover
        density="compact"
      />
    </Card>
  )
}
