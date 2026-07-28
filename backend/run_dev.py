"""Wrapper de desenvolvimento: garante que o processo rode com cwd=backend/
(para que o .env relativo seja encontrado), independentemente de onde o
comando uvicorn tenha sido disparado."""
import os

import uvicorn

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
