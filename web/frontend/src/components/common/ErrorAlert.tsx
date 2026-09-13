import { Section } from '@astryxdesign/core/Section'
import { HStack } from '@astryxdesign/core/Stack'
import { StatusDot } from '@astryxdesign/core/StatusDot'
import { Text } from '@astryxdesign/core/Text'

export function ErrorAlert({ message }: { message: string }) {
  return (
    <Section variant="muted" padding={3}>
      <HStack gap={2} align="center">
        <StatusDot variant="error" label="Error" />
        <span style={{ color: '#dc2626', fontSize: '0.875rem' }}>
          <Text>{message}</Text>
        </span>
      </HStack>
    </Section>
  )
}
