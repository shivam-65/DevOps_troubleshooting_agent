import { useLocation } from 'react-router-dom';
import { ConnectionStatus } from '@/components/shared/ConnectionStatus';
import { useWebSocket } from '@/contexts/WebSocketContext';

const pageTitles: Record<string, string> = {
  '/': 'Dashboard',
  '/incidents': 'Incidents',
  '/actions': 'Actions',
  '/reports': 'Reports',
  '/settings': 'Settings',
};

export function Header() {
  const location = useLocation();
  const { connected } = useWebSocket();

  const getTitle = () => {
    if (pageTitles[location.pathname]) return pageTitles[location.pathname];
    if (location.pathname.includes('/investigations/')) return 'Investigation Detail';
    if (location.pathname.match(/\/incidents\/.+/)) return 'Incident Detail';
    return 'Incident Commander';
  };

  return (
    <header className="h-14 border-b border-border flex items-center justify-between px-6 bg-card/50 backdrop-blur-sm sticky top-0 z-30">
      <h1 className="text-base font-semibold text-foreground">{getTitle()}</h1>
      <ConnectionStatus connected={connected} />
    </header>
  );
}
