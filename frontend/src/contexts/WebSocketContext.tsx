import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from 'react';

interface WebSocketContextType {
  connected: boolean;
  subscribe: (topic: string, callback: (msg: any) => void) => (() => void) | undefined;
}

const WebSocketContext = createContext<WebSocketContextType>({
  connected: false,
  subscribe: () => undefined,
});

export function WebSocketProvider({ children }: { children: ReactNode }) {
  const [connected, setConnected] = useState(false);
  const clientRef = useRef<any>(null);
  const subscriptionsRef = useRef<Map<string, Set<(msg: any) => void>>>(new Map());

  useEffect(() => {
    let cancelled = false;
    let reconnectTimeout: ReturnType<typeof setTimeout>;
    let reconnectDelay = 1000;

    async function connect() {
      try {
        const { Client } = await import('@stomp/stompjs');
        const SockJS = (await import('sockjs-client')).default;

        const client = new Client({
          webSocketFactory: () => new SockJS('/ws') as any,
          reconnectDelay: 0,
          onConnect: () => {
            if (cancelled) return;
            setConnected(true);
            reconnectDelay = 1000;
            subscriptionsRef.current.forEach((callbacks, topic) => {
              client.subscribe(topic, (message) => {
                try {
                  const body = JSON.parse(message.body);
                  callbacks.forEach((cb) => cb(body));
                } catch { /* ignore parse errors */ }
              });
            });
          },
          onDisconnect: () => {
            if (cancelled) return;
            setConnected(false);
          },
          onStompError: () => {
            if (cancelled) return;
            setConnected(false);
            reconnectTimeout = setTimeout(() => {
              reconnectDelay = Math.min(reconnectDelay * 2, 30000);
              connect();
            }, reconnectDelay);
          },
        });

        clientRef.current = client;
        client.activate();
      } catch {
        if (!cancelled) {
          reconnectTimeout = setTimeout(connect, reconnectDelay);
          reconnectDelay = Math.min(reconnectDelay * 2, 30000);
        }
      }
    }

    connect();

    return () => {
      cancelled = true;
      clearTimeout(reconnectTimeout);
      clientRef.current?.deactivate();
    };
  }, []);

  const subscribe = (topic: string, callback: (msg: any) => void) => {
    if (!subscriptionsRef.current.has(topic)) {
      subscriptionsRef.current.set(topic, new Set());
    }
    subscriptionsRef.current.get(topic)!.add(callback);

    const client = clientRef.current;
    let stompSub: any;
    if (client?.connected) {
      stompSub = client.subscribe(topic, (message: any) => {
        try {
          const body = JSON.parse(message.body);
          callback(body);
        } catch { /* ignore */ }
      });
    }

    return () => {
      subscriptionsRef.current.get(topic)?.delete(callback);
      stompSub?.unsubscribe();
    };
  };

  return (
    <WebSocketContext.Provider value={{ connected, subscribe }}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocket() {
  return useContext(WebSocketContext);
}
