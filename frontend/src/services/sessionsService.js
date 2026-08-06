import { api } from './api';

export const sessionsService = {
  async list() {
    const { data } = await api.get('/sessions');
    return data;
  },

  async upload(file, onProgress) {
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
