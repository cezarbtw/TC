import { api, USE_MOCK } from './api';
import { mockSessions, createMockSession } from '../utils/mockData';

const delay = (ms) => new Promise((r) => setTimeout(r, ms));

export const sessionsService = {
  async list() {
    if (USE_MOCK) {
      await delay(120);
      return [...mockSessions];
    }
    const { data } = await api.get('/sessions');
    return data;
  },

  async get(id) {
    if (USE_MOCK) {
      await delay(80);
      return mockSessions.find((s) => String(s.id) === String(id));
    }
    const { data } = await api.get(`/sessions/${id}`);
    return data;
  },

  async upload(file, onProgress) {
    if (USE_MOCK) {
      return new Promise((resolve) => {
        let progress = 0;
        const interval = setInterval(() => {
          progress += Math.random() * 12 + 3;
          if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
            onProgress?.(100);
            setTimeout(() => {
              const newSession = createMockSession(
                file.name,
                mockSessions.length + 1
              );
              mockSessions.unshift(newSession);
              resolve(newSession);
            }, 400);
          } else {
            onProgress?.(Math.floor(progress));
          }
        }, 300);
      });
    }

    const formData = new FormData();
    formData.append('file', file);
    const { data } = await api.post('/sessions/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (e.total) {
          onProgress?.(Math.floor((e.loaded * 100) / e.total));
        }
      },
    });
    return data;
  },
};
