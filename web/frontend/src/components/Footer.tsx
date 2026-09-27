import { Button, HStack, Text } from '@astryxdesign/core'
import { useStockStore, useShallow } from '@/stores'
import { APP_CONFIG } from '@/configs'

export function Footer() {
  const { themeMode, toggleThemeMode } = useStockStore(
    useShallow((state) => ({
      themeMode: state.themeMode,
      toggleThemeMode: state.toggleThemeMode,
    })),
  )

  const themeButtonLabel = themeMode === 'light' ? 'Dark Mode' : 'Light Mode'

  return (
    <HStack justify="between" align="center" gap={2}>
      <Text color="secondary">
        {APP_CONFIG.title}
      </Text>
      <Button
        variant="secondary"
        label={themeButtonLabel}
        onClick={toggleThemeMode}
      />
    </HStack>
  )
}
