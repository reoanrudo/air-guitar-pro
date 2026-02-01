# Air Guitar

モバイルでのコード選択とPCでのカメラ利用ストローク検出を組み合わせた、マルチプラットフォームエアギター体験。

## 概要

このプロジェクトは3つの連携するコンポーネントで構成されています：

- **air-guitar-left-hand** - モバイルアプリ（React Native/Expo）コード選択用
- **air-guitar-pro** - PC Webアプリ（React/Vite）カメラを使ったストローク検出
- **server** - Python WebSocket サーバー リアルタイム通信用

## アーキテクチャ

```
┌─────────────────┐     WebSocket      ┌──────────────┐     WebSocket      ┌─────────────────┐
│   モバイルアプリ │ ◄────────────────► │   サーバー   │ ◄────────────────► │   PC Webアプリ  │
│  (左手)         │                     │  (Python)    │                     │  (右手)         │
│  コード選択     │                     │  メッセージ  │                     │  カメラストローク│
└─────────────────┘                     │   中継       │                     └─────────────────┘
                                        └──────────────┘
```

## プロジェクト詳細

### air-guitar-left-hand（モバイル）

スマートフォンを縦持ちして、ギターコードを選択するアプリ。

**機能:**
- コード選択: C, G, D, Em, Am, F, Dm, A, E
- フレット位置の視覚的表示
- WebSocketによるリアルタイムデータ送信
- ダークモードUI（アンバー/オレンジテーマ）

**技術:** React Native, Expo Router, TypeScript, NativeWind

**起動方法:**
```bash
cd air-guitar-left-hand
npx expo start
```

### air-guitar-pro（PC）

ウェブカメラでハンドジェスチャーを検出してストロークをシミュレートするWebプレイヤー。

**機能:**
- TensorFlow.js handpose によるジェスチャー検出
- Tone.js 音声合成
- ノートスコアリングシステム（Perfect/Great/Miss）
- パーティクルエフェクト
- リーダーボード

**技術:** React 19, Vite, TensorFlow.js, Tone.js

**起動方法:**
```bash
cd air-guitar-pro
npm run dev
```

### server（Python）

モバイルとPCの間でメッセージを中継するWebSocketシグナリングサーバー。

**機能:**
- WebSocket メッセージ中継
- ルーム管理（有効期限付き）
- User-Agent によるデバイス検出
- ADB API エンドポイント
- MySQL データベース（Drizzle ORM）

**技術:** FastAPI, Uvicorn, SQLAlchemy, WebSockets

**起動方法:**
```bash
cd server
python scripts/run_server.py
```

## クイックスタート

```bash
# 依存関係のインストール
pnpm install

# 全サービス起動（Pythonサーバー + Metro）
pnpm dev

# 個別に起動:
pnpm dev:server:python  # Pythonサーバーのみ
pnpm dev:metro          # Metroバンドラーのみ
```

## ポート番号

| サービス | ポート |
|---------|-------|
| Python サーバー | 3000 |
| PC Web アプリ | 5173 |
| Metro バンドラー | 8081 |

## 動作環境

- Node.js 18+
- Python 3.8+
- MySQL データベース
- ADB（Android端末管理用）
