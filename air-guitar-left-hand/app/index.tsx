import React, { useState, useCallback, useEffect, useRef } from 'react';
import { Text, View, TouchableOpacity, Pressable, ScrollView } from 'react-native';
import { StatusBar } from 'expo-status-bar';

// コード定義（弦ごとのフレット位置）
const CHORDS = {
  C: { name: 'C', frets: [null, null, null, null, null, null] },
  'C (押さない)': { name: 'C (押さない)', frets: [-1, -1, -1, -1, -1, -1] },
  D: { name: 'D', frets: [null, -1, 0, 0, null, null] },
  G: { name: 'G', frets: [2, null, null, 0, 0, null] },
  'G (開放弦)': { name: 'G (開放弦)', frets: [-1, -1, -1, -1, -1, -1] },
  Em: { name: 'Em', frets: [0, 2, 2, 0, null, null] },
  Am: { name: 'Am', frets: [null, 0, 2, 2, 1, null] },
  F: { name: 'F', frets: [null, null, null, 2, null, null] },
};

export default function GuitarScreen() {
  const [selectedChord, setSelectedChord] = useState<string>('C (押さない)');
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const fretStatesRef = useRef<(number | null)[]>([-1, -1, -1, -1, -1, -1]);

  // WebSocket接続
  useEffect(() => {
    const ws = new WebSocket('ws://10.201.98.196:3000/ws');
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('✅ Connected to server');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      console.log('📩 Received:', event.data);
    };

    ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      setIsConnected(false);
    };

    ws.onclose = () => {
      console.log('🔌 Disconnected');
      setIsConnected(false);
      // 5秒後に再接続
      setTimeout(() => {
        console.log('🔄 Reconnecting...');
      }, 5000);
    };

    return () => {
      ws.close();
    };
  }, []);

  // コード変更を送信
  const sendChordChange = useCallback((chordName: string, frets: (number | null)[]) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.warn('⚠️ WebSocket not connected');
      return;
    }

    const message = {
      type: 'chord_change',
      chord: chordName,
      frets: frets,
      timestamp: Date.now(),
    };

    console.log('📤 Sending:', message);
    wsRef.current.send(JSON.stringify(message));
    fretStatesRef.current = frets;
  }, []);

  // 開放弦を送信
  const sendOpenStrings = useCallback(() => {
    const message = {
      type: 'chord_change',
      chord: '開放弦',
      frets: [-1, -1, -1, -1, -1, -1],
      timestamp: Date.now(),
    };
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  return (
    <View style={{ flex: 1, backgroundColor: '#1a1a1a' }}>
      <StatusBar style={{ backgroundColor: '#1a1a1a' }} />

      {/* ヘッダー */}
      <View style={{ paddingTop: 60, paddingHorizontal: 20, paddingBottom: 20 }}>
        <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
          <Text style={{ color: '#fff', fontSize: 24, fontWeight: 'bold' }}>
            Air Guitar Left
          </Text>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
            <View style={{
              width: 12, height: 12, borderRadius: 6,
              backgroundColor: isConnected ? '#22c55e' : '#ef4444'
            }} />
            <Text style={{ color: isConnected ? '#22c55e' : '#ef4444', fontSize: 14 }}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </Text>
          </View>
        </View>

        {/* 現在のコード */}
        <View style={{ marginTop: 30, alignItems: 'center' }}>
          <Text style={{ color: '#888', fontSize: 14 }}>現在のコード</Text>
          <Text style={{ color: '#fff', fontSize: 48, fontWeight: 'bold', marginTop: 10 }}>
            {selectedChord}
          </Text>
        </View>
      </View>

      {/* コード選択エリア */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={{ paddingHorizontal: 10 }}
        contentContainerStyle={{ gap: 10 }}
      >
        {Object.entries(CHORDS).map(([key, chord]) => (
          <TouchableOpacity
            key={key}
            onPress={() => {
              setSelectedChord(chord.name);
              sendChordChange(chord.name, chord.frets);
            }}
            style={{
              paddingHorizontal: 20,
              paddingVertical: 15,
              backgroundColor: selectedChord === chord.name ? '#d97706' : '#333',
              borderRadius: 12,
              minWidth: 100,
              alignItems: 'center',
            }}
          >
            <Text style={{ color: '#fff', fontSize: 16, fontWeight: 'bold' }}>
              {chord.name}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* 弦の表示 */}
      <View style={{ flex: 1, justifyContent: 'center', paddingHorizontal: 20 }}>
        <View style={{ gap: 25 }}>
          {[0, 1, 2, 3, 4, 5].map((stringIndex) => (
            <View
              key={stringIndex}
              style={{
                flexDirection: 'row',
                alignItems: 'center',
                gap: 10,
              }}
            >
              <Text style={{ color: '#888', fontSize: 16, width: 30 }}>
                {6 - stringIndex}
              </Text>
              <View
                style={{
                  flex: 1,
                  height: 8,
                  backgroundColor: fretStatesRef.current[stringIndex] !== null
                    ? '#22c55e'
                    : '#333',
                  borderRadius: 4,
                }}
              />
              <Text style={{ color: '#888', fontSize: 12, width: 60 }}>
                {fretStatesRef.current[stringIndex] !== null
                  ? `Fret ${fretStatesRef.current[stringIndex]}`
                  : 'Open'}
                </Text>
            </View>
          ))}
        </View>
      </View>

      {/* 開放弦ボタン */}
      <View style={{ padding: 20 }}>
        <TouchableOpacity
          onPress={sendOpenStrings}
          style={{
            backgroundColor: '#333',
            paddingVertical: 20,
            borderRadius: 12,
            alignItems: 'center',
          }}
        >
          <Text style={{ color: '#fff', fontSize: 18, fontWeight: 'bold' }}>
            開放弦
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}
