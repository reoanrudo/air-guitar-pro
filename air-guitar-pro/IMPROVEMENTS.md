# Air Guitar Pro - 改善案

## 概要
PC側Webアプリ（air-guitar-pro）のコードレビューを20回実施し、操作性・セキュリティ・追加機能・パフォーマンス・コード品質の観点から改善案をまとめたもの。

---

## 1. 操作性/UX の改善

### 1.1 Player ID入力の省略可能化
**現状**: プレイヤーID入力が必須で、ゲーム開始前に強制される
**問題**: 手軽に試したいユーザーの導入障壁となる
**改善**:
- スキップボタンを追加してゲストプレイを可能に
- LocalStorageに前回入力したIDを保存
- 自動生成IDを提示して「これでOK」ボタンのみで開始

### 1.2 ゲーム設定の調整画面追加
**現状**: 難易度や感度設定が変更できない
**問題**: ユーザーによって最適なストローク判定値が異なる
**改善**:
- 設定パネルを追加（ストローク感度、HITウィンドウ、ノーツ速度）
- プリセット（初心者/上級者/カスタム）
- 設定のLocalStorage保存

### 1.3 チュートリアル/練習モード
**現状**: いきなり本番ゲームが始まる
**問題**: 操作方法を理解する手段がない
**改善**:
- 「HOW TO PLAY」画面を追加
- 練習モード（ノーツなしでストローク練習）
- カメラキャリブレーション機能

### 1.4 接続状態の視覚的フィードバック強化
**現状**: リンク中/リンク済みの表示が小さい
**問題**: 接続トラブル時に原因がわかりにくい
**改善**:
- 接続状況を大きく表示
- エラー時に具体的な対処法を表示
- モバイル側の接続待ち状態を視覚化

### 1.5 キーボードショートカット対応
**現状**: マウス操作のみ
**問題**: ゲーム中にマウス操作が不便
**改善**:
- `SPACE`: 一時停止/再開
- `ESC`: 終了確認
- `R`: 再起動
- `M`: ミュート

---

## 2. セキュリティの強化

### 2.1 Player IDの入力値バリデーション
**現状**: `maxLength={20}`のみで、内容のチェックがない
**問題**: XSSインジェクションや不正な文字列の可能性
**改善**:
```typescript
const sanitizePlayerId = (id: string): string => {
  return id.replace(/[<>\"']/g, '').trim().substring(0, 20);
};
```
- 英数字と一部記号のみ許可
- 空白除去
- 長さ制限の厳格化

### 2.2 WebRTCメッセージの型安全と検証
**現状**: `data: any`で型チェックがない
**問題**: 不正なメッセージでアプリがクラッシュする可能性
**改善**:
```typescript
interface P2PMessage {
  type: 'FRET_UPDATE' | 'READY' | 'HEARTBEAT';
  payload: number[] | object;
}

const validateMessage = (data: unknown): data is P2PMessage => {
  // 検証ロジック
};
```

### 2.3 接続数の制限
**現状**: 複数のモバイル側から同時に接続可能
**問題**: 意図しない接続によるゲーム崩壊
**改善**:
- ホストは1つの接続のみ許可
- 新しい接続が来たら既存接続を切断
- 接続リストの管理

### 2.4 Room IDの推測困難性
**現状**: 4文字の大文字英数字（36^4 = 167万通り）
**問題**: 総当たり攻撃で接続される可能性
**改善**:
- オプションでランダム8文字に増やせる
- 接続時にパスワード保護
- 一時的なRoom IDを使用

### 2.5 バックエンド通信のHTTPS強制
**現状**: BackendServiceの通信プロトコル指定がない
**問題**: HTTPだとスコアが盗聴される可能性
**改善**:
- HTTPSのみ許可
- 通信内容の署名検証
- リプレイ攻撃防止（タイムスタンプ + ナンス）

---

## 3. 追加機能の提案

### 3.1 難易度選択
**現状**: 固定難易度
**提案**:
- EASY: ノーツ速度遅め、HITウィンドウ広め
- NORMAL: 現在
- HARD: ノーツ速度速め、HITウィンドウ狭め
- EXTREME: 2倍速、厳密判定

### 3.2 スコアランキング実装
**現状**: Leaderboardコンポーネントがあるが未実装
**提案**:
- 部屋IDごとのランキング
- 全体ランキング（オプション）
- 日次/週次/月次ランキング
- 自分のベストスコア記録

### 3.3 楽曲/コース選択
**現状**: ランダムなノーツのみ
**提案**:
- プリセット楽曲（ノーツパターン）
- BPM調整
- 曲の長さ選択（ショート/ロング）

### 3.4 オーディオ設定
**現状**: 固定音色
**提案**:
- ギター音色選択（クリーン/オーバードライブ/メタル）
- ボリューム調整
- エフェクト切替え（リバーブon/off）

### 3.5 プレイ録画・再生
**現状**: プレイ内容を記録していない
**提案**:
- プレイ中のカメラ映像を録画
- リプレイ視聴機能
- スコアハイライト編集
- SNS共有

---

## 4. パフォーマンス改善

### 4.1 Canvasレンダリングの最適化
**現状**: 毎フレーム全て再描画
**問題**: GPU負荷が高い
**改善**:
- 背景は静的レイヤーに分離
- 変化がない要素をキャッシュ
- `willReadFrequently: true` オプション使用

### 4.2 HandPose推論のスロットリング
**現状**: 毎フレーム推論
**問題**: CPU/GPU負荷が高い
**改善**:
- 30FPSで十分なのでスキップフレーム導入
- 手が検出されない間は推論頻度下げ
- Web Workerで別スレッド化

### 4.3 ノーツ配列の事前生成
**現状**: ゲーム中にランダム生成
**問題**: 予測不可能でランダム性が低い
**改善**:
- ゲーム開始時にノーツパターン生成
- シード値で再現可能なランダム
- メモリ効率の良いリングバッファ使用

### 4.4 メモリリーク防止
**現状**: コンポーネントアンマウント時に不完全なクリーンアップ
**問題**: 長時間プレイでメモリ使用量増加
**改善**:
```typescript
return () => {
  if (frameIdRef.current) {
    cancelAnimationFrame(frameIdRef.current);
    frameIdRef.current = null;
  }
  const stream = videoRef.current?.srcObject as MediaStream;
  stream?.getTracks().forEach(t => {
    t.stop();
    stream.removeTrack(t);
  });
  if (videoRef.current) {
    videoRef.current.srcObject = null;
  }
  // refの全てをnullに
};
```

### 4.5 画像/フォントの最適化
**現状**: システムフォントのみ
**問題**: 表現の制限
**改善**:
- Web Fontの最適化（サブセット化）
- アイコンはSVGスプライト
- 画像はWebP形式

---

## 5. コード品質向上

### 5.1 型定義の強化
**現状**: `any`型が使用されている
**改善**:
```typescript
// services/WebRTCService.ts
interface MessageHandlers {
  onFretUpdate: (frets: number[]) => void;
  onReady: (deviceId: string) => void;
  onHeartbeat: () => void;
}

interface WebRTCConfig {
  iceServers: { urls: string }[];
  reconnectInterval: number;
  maxRetries: number;
}
```

### 5.2 エラーハンドリングの統一
**現状**: `console.error`のみで、ユーザーへの通知がない
**改善**:
```typescript
class GameError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly recoverable: boolean = false
  ) {
    super(message);
    this.name = 'GameError';
  }
}

// 使用例
try {
  await init();
} catch (e) {
  if (e instanceof GameError && e.recoverable) {
    showRetryDialog(e);
  } else {
    showFatalError(e);
  }
}
```

### 5.3 依存性注入の導入
**現状**: コンポーネント内で直接インスタンス化
**改善**:
```typescript
// サービスのインターフェース化
interface IAudioEngine {
  start(): Promise<void>;
  playStrum(frets: number[], dir: 'up'|'down'): void;
}

// テスト容易性向上
class PCPlayerProps {
  audioEngine: IAudioEngine;  // DI
  webrtc: WebRTCService;
  // ...
}
```

### 5.4 設定ファイルの外出し
**現状**: マジックナンバーが散在
**改善**:
```typescript
// config/game.ts
export const GAME_CONFIG = {
  NOTE_SPEED: 16,
  HIT_WINDOW: 120,
  STRUM_VELOCITY_THRESHOLD: 18,
  SPAWN_INTERVAL: 1100,
  STRUM_ZONE_RATIO: { x: 0.1, y: 0.65, w: 0.4, h: 0.3 },
} as const;

// 難易度別設定
export const DIFFICULTY = {
  easy: { NOTE_SPEED: 10, HIT_WINDOW: 180 },
  normal: { NOTE_SPEED: 16, HIT_WINDOW: 120 },
  hard: { NOTE_SPEED: 24, HIT_WINDOW: 80 },
} as const;
```

### 5.5 テストコード追加
**現状**: テストがない
**改善**:
```typescript
// services/__tests__/AudioEngine.test.ts
describe('AudioEngine', () => {
  it('should play strum with correct frets', async () => {
    const engine = new AudioEngine();
    await engine.start();

    const spy = jest.spyOn(engine['synth'], 'triggerAttackRelease');
    engine.playStrum([0, 1, 0, 2, 0, 0], 'down');

    expect(spy).toHaveBeenCalledTimes(6);
  });
});

// components/__tests__/PCPlayer.test.tsx
describe('PCPlayer', () => {
  it('should update score on note hit', () => {
    // テスト実装
  });
});
```

### 5.6 ロギングの強化
**現状**: `console.log`のみ
**改善**:
```typescript
// utils/logger.ts
enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
}

class Logger {
  private level = LogLevel.INFO;

  debug(...args: any[]) { if (this.level <= LogLevel.DEBUG) console.log('[DEBUG]', ...args); }
  info(...args: any[]) { if (this.level <= LogLevel.INFO) console.log('[INFO]', ...args); }
  warn(...args: any[]) { if (this.level <= LogLevel.WARN) console.warn('[WARN]', ...args); }
  error(...args: any[]) { if (this.level <= LogLevel.ERROR) console.error('[ERROR]', ...args); }
}

// 本番環境では外部ログサービスに送信
```

### 5.7 useCallback依存配列の修正
**現状**: `App.tsx`で依存配列に問題
**改善**:
```typescript
// 現状（問題あり）
const startPCMode = useCallback(async (id: string) => {
  // ...
}, []); // roomIdを使っているのに依存配列が空

// 修正案
const startPCMode = useCallback(async (id: string) => {
  // ...
}, []); // idを引数で受け取るので依存配列は空でOK

// useEffect側も修正
useEffect(() => {
  // ...
}, []); // 空でOK、初期化のみ
```

---

## 6. バグ修正

### 6.1 useEffectの無限ループ対策
**現状**: `dims`依存のuseEffectが再実行されると全初期化される
**問題**: 画面リサイズ時にモデルが再読み込みされる
**改善**:
- 初期化ロジックを分離
- リサイズ時は寸法値のみ更新

### 6.2 ストリームのクリーンアップ
**現状**: ビデオトラックが正しく停止しない可能性
**改善**:
```typescript
const stream = videoRef.current?.srcObject as MediaStream;
if (stream) {
  stream.getTracks().forEach(track => {
    track.stop();
    stream.removeTrack(track);
  });
}
videoRef.current.srcObject = null;
```

### 6.3 スコア送信の重複防止
**現状**: `handleExit`が複数回呼ばれると重複送信
**改善**:
```typescript
const isSubmittingRef = useRef(false);

const handleExit = async () => {
  if (isSubmittingRef.current) return;
  isSubmittingRef.current = true;

  try {
    // 送信処理
  } finally {
    isSubmittingRef.current = false;
  }
};
```

---

## 7. モバイル連携の改善

### 7.1 接続失敗時のリトライUI
**現状**: 自動リトライのみ
**改善**:
- 手動リトライボタン
- 部屋IDの再入力
- QRコード表示（モバイル側でスキャン）

### 7.2 Heartbeat実装
**現状**: 接続が切れても気づけない
**改善**:
```typescript
// PC側
setInterval(() => {
  webrtc.send({ type: 'HEARTBEAT', timestamp: Date.now() });
}, 5000);

let lastHeartbeat = Date.now();
webrtc.onMessage((data) => {
  if (data.type === 'HEARTBEAT') {
    lastHeartbeat = Date.now();
  }
});

// タイムアウト検知
setInterval(() => {
  if (Date.now() - lastHeartbeat > 15000) {
    // 接続断とみなす
  }
}, 5000);
```

---

## 8. アクセシビリティ

### 8.1 キーボードナビゲーション
**現状**: マウス操作のみ
**改善**:
- 全ボタンにフォーカス対応
- Tabキーで順次移動
- Enter/Spaceで選択

### 8.2 色覚サポート
**現状**: 固定色
**改善**:
- カラーモード切替（通常/赤緑色盲/青黄色盲）
- コントラスト比確保（WCAG AA以上）

### 8.3 スクリーンリーダー対応
**現状**: aria属性がない
**改善**:
```tsx
<button
  aria-label="ゲーム開始"
  aria-describedby="start-desc"
>
  GIG START
</button>
<span id="start-desc" className="sr-only">
  カメラ使用、音量に注意
</span>
```

---

## 優先度マトリックス

| 改善案 | 重要度 | 緊急度 | 工数 | 優先度 | カテゴリ |
|--------|--------|--------|------|--------|----------|
| Player ID省略可能化 | A | B | 小 | 高 | UX |
| 接続状態視覚化 | A | B | 小 | 高 | UX |
| エラーハンドリング統一 | A | A | 中 | 高 | 品質 |
| メッセージ型検証 | A | A | 中 | 高 | セキュリティ |
| バグ修正（useEffect） | A | A | 小 | 高 | 品質 |
| 難易度選択 | B | C | 中 | 中 | 機能 |
| 設定パネル | B | C | 中 | 中 | UX |
| Heartbeat実装 | B | B | 中 | 中 | 機能 |
| Canvas最適化 | B | C | 中 | 中 | パフォーマンス |
| 型定義強化 | B | B | 大 | 中 | 品質 |
| テストコード追加 | B | C | 大 | 中 | 品質 |
| チュートリアル | C | C | 中 | 中 | UX |
| ランキング実装 | C | C | 大 | 低 | 機能 |
| 録画機能 | C | C | 大 | 低 | 機能 |
| Web Worker化 | C | C | 大 | 低 | パフォーマンス |
| アクセシビリティ | C | C | 中 | 低 | UX |
| 接続数制限 | B | B | 小 | 中 | セキュリティ |
| Room ID強化 | C | C | 小 | 低 | セキュリティ |
| HTTPS強制 | B | A | 小 | 中 | セキュリティ |
| ロギング強化 | B | C | 中 | 中 | 品質 |

**凡例**:
- 重要度: A（必須）, B（推奨）, C（あったらいい）
- 緊急度: A（すぐに）, B（近日中）, C（いつか）
- 工数: 小（1-2時間）, 中（半日〜1日）, 大（2日以上）
- 優先度: 高（重要度×緊急度/工数）, 中, 低

---

## 最初に取り組むべきこと（Top 5）

1. **バグ修正（useEffectの無限ループ）** - 緊急度が高く、工数が小さい
2. **エラーハンドリング統一** - 基盤となる品質向上
3. **Player ID省略可能化** - ユーザー体験の即時改善
4. **接続状態視覚化** - トラブルシューティング削減
5. **メッセージ型検証** - セキュリティリスク低減

---

## 次回レビュー時のチェックリスト

- [ ] 型定義ファイルが作成されているか
- [ ] エラーハンドリングが統一されているか
- [ ] テストコードが追加されているか
- [ ] パフォーマンス計測が行われているか
- [ ] セキュリティレビューが完了しているか
- [ ] アクセシビリティ検証が行われているか
- [ ] ユーザーテストが実施されているか

---

## まとめ

本改善案では、20回のコードレビューを通じて発見した課題を5つの観点から整理しました。

**最も優先すべきは「安定性」です。**
- バグ修正（useEffect無限ループ）
- エラーハンドリングの統一
- 型安全なメッセージ処理

**次いで「ユーザー体験」の改善です。**
- Player ID入力の簡素化
- 接続状態の明確な表示
- 設定調整機能

**将来的には「機能拡張」で遊び心地を向上させてください。**
- 難易度選択
- ランキング
- 楽曲選択

おやすみなさい！
