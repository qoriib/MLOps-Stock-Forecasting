import { Card } from '@astryxdesign/core/Card'
import { HStack } from '@astryxdesign/core/Stack'
import { Spinner } from '@astryxdesign/core/Spinner'
import { Text } from '@astryxdesign/core/Text'

interface LoadingIndicatorProps {
  label?: string
  isCard?: boolean
}

export function LoadingIndicator({
  label = 'Memuat data...',
  isCard = false,
}: LoadingIndicatorProps) {
  const content = (
    <HStack gap={3} align="center" justify="center">
      <Spinner label={label} />
      <Text color="secondary" size="sm">
        {label}
      </Text>
    </HStack>
  )

  if (isCard) {
    return (
      <Card variant="default" padding={4}>
        {content}
      </Card>
    )
  }

  return content
}
