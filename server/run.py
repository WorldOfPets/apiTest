"""Удобный запуск: ``python run.py`` стартует Uvicorn с логированием доступа."""

import uvicorn

from app.config import HOST, PORT

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=False,
        access_log=True,
    )
