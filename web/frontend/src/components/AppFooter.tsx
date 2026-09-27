import { HStack, Text } from '@astryxdesign/core'
import { APP_CONFIG } from '@/configs'

export function AppFooter() {
  return (
    <HStack justify="between" align="center" wrap="wrap" gap={2}>
      <Text color="secondary" size="sm">
        {APP_CONFIG.title} — Arsitektur MLOps Terpadu (Single Unified Chart)
      </Text>
      <Text color="secondary" size="xsm">
        Powered by Beanie ODM, FastAPI, and Deep Learning (LSTM & GRU)
      </Text>
    </HStack>
  )
}
