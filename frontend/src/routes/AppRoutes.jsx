import { Route, Routes } from 'react-router-dom';
import { MainLayout } from '../components/layout/MainLayout';
import { Dashboard } from '../pages/Dashboard';
import { Sessions } from '../pages/Sessions';
import { Upload } from '../pages/Upload';
import { NotFound } from '../pages/NotFound';
import { Login } from '../pages/Login';
import { ProtectedRoute } from './ProtectedRoute';

export function AppRoutes() {
  return (
    <Routes>
      <Route path="login" element={<Login />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<MainLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="sessions" element={<Sessions />} />
          <Route path="upload" element={<Upload />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Route>
    </Routes>
  );
}
