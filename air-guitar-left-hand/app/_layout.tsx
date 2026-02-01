import { Stack } from 'expo-router';
import { useEffect } from 'react';

export default function RootLayout() {
  useEffect(() => {
    // スリープモードを無効化
    if (typeof window !== 'undefined') {
      window.addEventListener('error', (e) => {
        console.error('Global error:', e);
      });
    }
  }, []);

  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="index" options={{ title: 'Guitar' }} />
    </Stack>
  );
}
