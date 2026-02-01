
import Peer, { DataConnection } from 'peerjs';

export class WebRTCService {
  private peer: Peer | null = null;
  private connection: DataConnection | null = null;
  private roomId: string;
  private onMessageCallback: ((data: any) => void) | null = null;
  private onConnectedCallback: (() => void) | null = null;
  private isHost: boolean = false;

  constructor(roomId: string) {
    this.roomId = roomId;
  }

  async initialize(isHost: boolean): Promise<void> {
    this.isHost = isHost;
    const peerId = isHost ? `AIR-GUITAR-PC-${this.roomId}` : undefined;
    
    // PeerJSの設定。ローカルシグナリングサーバーに接続
    this.peer = new Peer(peerId, {
      debug: 1,
      host: 'localhost',
      port: 3001,
      path: '/peerjs',
      config: {
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' },
          { urls: 'stun:stun1.l.google.com:19302' }
        ]
      }
    });

    this.peer.on('open', (id) => {
      console.log('Peer ID is: ' + id);
      if (!isHost) {
        this.connectToHost();
      }
    });

    this.peer.on('disconnected', () => {
      console.warn('Peer disconnected from server. Attempting to reconnect...');
      this.peer?.reconnect();
    });

    this.peer.on('error', (err) => {
      console.error('PeerJS Error:', err.type, err.message);
      // 'peer-unavailable' はホストがまだ立ち上がっていない場合によく出る
      if (err.type === 'peer-unavailable') {
        if (!isHost) {
          console.log('Host not available. Retrying in 3 seconds...');
          setTimeout(() => this.connectToHost(), 3000);
        }
      } else if (err.type === 'network') {
        // ネットワーク断絶などの場合
        setTimeout(() => this.peer?.reconnect(), 5000);
      }
    });

    if (isHost) {
      this.peer.on('connection', (conn) => {
        // 既存の接続があれば閉じる（新しい接続を優先）
        if (this.connection) {
          this.connection.close();
        }
        this.connection = conn;
        this.setupConnection();
        this.onConnectedCallback?.();
      });
    }
  }

  private connectToHost() {
    if (!this.peer || this.peer.destroyed) return;
    
    const targetId = `AIR-GUITAR-PC-${this.roomId}`;
    console.log(`Connecting to host: ${targetId}`);
    
    this.connection = this.peer.connect(targetId, {
      reliable: true
    });

    this.setupConnection();
    
    this.connection.on('open', () => {
      console.log('Connection to host opened');
      this.onConnectedCallback?.();
    });
  }

  private setupConnection() {
    if (!this.connection) return;

    this.connection.on('data', (data) => {
      this.onMessageCallback?.(data);
    });

    this.connection.on('close', () => {
      console.log('Data connection closed');
      // 切断された場合は再接続を試みる（コントローラー側のみ）
      if (!this.isHost) {
        setTimeout(() => this.connectToHost(), 2000);
      }
    });

    this.connection.on('error', (err) => {
      console.error('DataConnection Error:', err);
    });
  }

  onMessage(callback: (data: any) => void) {
    this.onMessageCallback = callback;
  }

  onConnected(callback: () => void) {
    this.onConnectedCallback = callback;
  }

  send(data: any) {
    if (this.connection && this.connection.open) {
      this.connection.send(data);
    }
  }

  disconnect() {
    this.connection?.close();
    this.peer?.destroy();
  }
}
