import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';
import { DashboardPage } from '@/pages/DashboardPage';
import { IncidentsListPage } from '@/pages/IncidentsListPage';
import { IncidentDetailPage } from '@/pages/IncidentDetailPage';
import { InvestigationDetailPage } from '@/pages/InvestigationDetailPage';
import { ActionsPage } from '@/pages/ActionsPage';
import { ReportsPage } from '@/pages/ReportsPage';
import { SettingsPage } from '@/pages/SettingsPage';
import { NotFoundPage } from '@/pages/NotFoundPage';
import { WebSocketProvider } from '@/contexts/WebSocketContext';

function App() {
  return (
    <BrowserRouter>
      <WebSocketProvider>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            <Route index element={<DashboardPage />} />
            <Route path="incidents" element={<IncidentsListPage />} />
            <Route path="incidents/:id" element={<IncidentDetailPage />} />
            <Route path="incidents/:id/investigations/:investigationId" element={<InvestigationDetailPage />} />
            <Route path="actions" element={<ActionsPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </WebSocketProvider>
    </BrowserRouter>
  );
}

export default App;
