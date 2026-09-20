import { UnifiedTwinState } from '../types';

export type WebSocketStatus = 'CONNECTING' | 'CONNECTED' | 'DISCONNECTED' | 'RECONNECTING';

export class TwinWebSocketClient {
  private url: string;
  private ws: WebSocket | null = null;
  private reconnectTimeout: any = null;
  private pingInterval: any = null;
  private onMessageCallback: ((data: UnifiedTwinState) => void) | null = null;
  private onStatusCallback: ((status: WebSocketStatus) => void) | null = null;
  private isDestroyed = false;

  constructor(url: string = 'ws://localhost:8000/ws/telemetry') {
    this.url = url;
  }

  public connect(
    onMessage: (data: UnifiedTwinState) => void,
    onStatus?: (status: WebSocketStatus) => void
  ) {
    this.onMessageCallback = onMessage;
    if (onStatus) this.onStatusCallback = onStatus;
    this.isDestroyed = false;
    this._initWs();
  }

  private _initWs() {
    if (this.isDestroyed) return;

    this.onStatusCallback?.('CONNECTING');
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.onStatusCallback?.('CONNECTED');
        // Start ping heartbeat
        this.pingInterval = setInterval(() => {
          if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send('ping');
          }
        }, 15000);
      };

      this.ws.onmessage = (event) => {
        if (event.data === 'pong') return;
        try {
          const parsed: UnifiedTwinState = JSON.parse(event.data);
          this.onMessageCallback?.(parsed);
        } catch (err) {
          console.error('[Twin WS] Parse error:', err);
        }
      };

      this.ws.onclose = () => {
        this._cleanupSockets();
        if (!this.isDestroyed) {
          this.onStatusCallback?.('RECONNECTING');
          this.reconnectTimeout = setTimeout(() => this._initWs(), 2000);
        } else {
          this.onStatusCallback?.('DISCONNECTED');
        }
      };

      this.ws.onerror = () => {
        this.ws?.close();
      };
    } catch (err) {
      this.onStatusCallback?.('RECONNECTING');
      this.reconnectTimeout = setTimeout(() => this._initWs(), 3000);
    }
  }

  private _cleanupSockets() {
    if (this.pingInterval) clearInterval(this.pingInterval);
    if (this.reconnectTimeout) clearTimeout(this.reconnectTimeout);
    this.pingInterval = null;
  }

  public disconnect() {
    this.isDestroyed = true;
    this._cleanupSockets();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.onStatusCallback?.('DISCONNECTED');
  }
}
