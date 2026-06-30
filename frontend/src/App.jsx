import { BrowserRouter } from 'react-router-dom';
import { SessionsProvider } from './context/SessionsContext';
import { ToastProvider } from './context/ToastContext';
import { AppRoutes } from './routes/AppRoutes';
import './components/charts/chartSetup';

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <SessionsProvider>
          <AppRoutes />
        </SessionsProvider>
      </ToastProvider>
    </BrowserRouter>
  );
}
