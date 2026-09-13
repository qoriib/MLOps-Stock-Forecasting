import { Card } from '@astryxdesign/core/Card'
import { Toolbar } from '@astryxdesign/core/Toolbar'
import { Heading } from '@astryxdesign/core/Heading'
import { Text } from '@astryxdesign/core/Text'
import { HStack } from '@astryxdesign/core/Stack'
import { Button } from '@astryxdesign/core/Button'
import { Selector } from '@astryxdesign/core/Selector'

interface ForecastControlsProps {
  ticker: string
  steps: string
  onStepsChange: (steps: string) => void
  loading: boolean
  onPredict: () => void
}

const STEP_OPTIONS = [
  { value: '7', label: '7 Hari' },
  { value: '14', label: '14 Hari' },
  { value: '30', label: '30 Hari' },
  { value: '60', label: '60 Hari' },
  { value: '90', label: '90 Hari' },
]

export function ForecastControls({
  ticker,
  steps,
  onStepsChange,
  loading,
  onPredict,
}: ForecastControlsProps) {
  return (
    <Card variant="default" padding={0}>
      <Toolbar
        label="Konfigurasi Peramalan"
        size="sm"
        startContent={
          <HStack gap={2} align="center">
            <Heading level={4}>Peramalan Saham</Heading>
            <Text color="secondary" size="sm">
              ({ticker || 'Memuat...'})
            </Text>
          </HStack>
        }
        endContent={
          <HStack gap={2} align="center">
            <Selector
              label="Horizon"
              isLabelHidden
              options={STEP_OPTIONS}
              value={steps}
              onChange={onStepsChange}
              width={120}
              size="sm"
            />
            <Button
              label="Jalankan Inferensi"
              variant="primary"
              size="sm"
              isLoading={loading}
              isDisabled={!ticker || loading}
              onClick={onPredict}
            />
          </HStack>
        }
      />
    </Card>
  )
}
