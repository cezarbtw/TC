# EmotionLens — React + Vite


## Stack
- React 18 + Vite
- React Router DOM
- Axios
- react-chartjs-2 + Chart.js
- CSS puro modularizado

## Como rodar
```bash
npm install
npm run dev
```

App em `http://localhost:5173`.

## Variáveis de ambiente
Veja `.env.example`:
- `VITE_API_URL` — endpoint do FastAPI
- `VITE_USE_MOCK` — `true` para usar dados mock, `false` para consumir a API

## Estrutura
```
src/
  assets/
  components/
    layout/      Sidebar, Header, MainLayout
    ui/          Button, Card, EmotionTag, ConfidenceBar, Skeleton, Icon
    charts/      TimelineChart, DonutChart
    dashboard/   StatCard, ProbabilityList, MiniSessions, ChartRangeControls
    sessions/    SessionsTable
    upload/      UploadArea, UploadProgress, UploadSuccess
  context/       SessionsContext, ToastContext
  hooks/         useUpload, useMediaQuery
  pages/         Dashboard, Sessions, Upload, NotFound
  routes/        AppRoutes
  services/      api (Axios), sessionsService
  styles/        tokens, base, layout, components, pages
  utils/         constants, formatters, mockData
  App.jsx
  main.jsx
```

## Integração futura com FastAPI
- `src/services/api.js` cria a instância Axios com `VITE_API_URL`.
- `src/services/sessionsService.js` expõe `list/get/upload`. Quando `VITE_USE_MOCK=false`, chama:
  - `GET  /sessions`
  - `GET  /sessions/:id`
  - `POST /sessions/upload` (multipart/form-data)
