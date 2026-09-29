import { BrowserRouter } from 'react-router-dom';
import { SessionsProvider } from './context/SessionsContext';
import { ToastProvider } from './context/ToastContext';
import { AppRoutes } from './routes/AppRoutes';
import { AuthProvider } from './context/AuthContext';
import './components/charts/chartSetup';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <SessionsProvider>
            <AppRoutes />
          </SessionsProvider>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
