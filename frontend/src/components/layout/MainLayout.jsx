import { useEffect, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { useMediaQuery } from '../../hooks/useMediaQuery';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

const TITLES = {
  '/': 'Dashboard',
  '/sessions': 'Sessões',
  '/upload': 'Upload de Vídeo',
};

function resolveTitle(pathname) {
  if (pathname.startsWith('/sessions')) return 'Sessões';
  if (pathname.startsWith('/upload')) return 'Upload de Vídeo';
  return TITLES[pathname] || 'Dashboard';
}

export function MainLayout() {
  const location = useLocation();
  const isMobile = useMediaQuery('(max-width: 768px)');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    setSidebarOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    if (!isMobile) setSidebarOpen(false);
  }, [isMobile]);

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape') setSidebarOpen(false);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  return (
    <>
      <Sidebar
        open={isMobile && sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />
      <main className="main-content">
        <Header
          title={resolveTitle(location.pathname)}
          onMenuClick={() => setSidebarOpen((v) => !v)}
        />
        <section className="view">
          <Outlet />
        </section>
      </main>
    </>
  );
}
