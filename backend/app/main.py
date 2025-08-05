from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from prometheus_fastapi_instrumentator import Instrumentator

# ───── Menambahkan path root proyek ke sys.path ─────
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, project_root)

# ───── Import prometheus ─────
from backend.app.routes.metrics_routes import router as metrics_router

# ───── Import semua router ─────
from backend.app.routes.calculator_routes import router as calculator_router
from backend.app.routes.dandur_routes import router as dandur_router
from backend.app.routes.danpen_routes import router as danpen_router
from backend.app.routes.barangimpian_routes import router as barangimpian_router
from backend.app.routes.user_routes import router as user_router
from backend.app.routes.transaction_routes import router as transaction_router
from backend.app.routes.category_routes import router as category_router
from backend.app.routes.analysis_routes import router as analysis_router

# ───── Database ─────
from backend.app.database.database_conn import engine, Base
from backend.app.database import models  # penting agar model dikenali oleh Base.metadata

# ───── Inisialisasi FastAPI App ─────
app = FastAPI(
    title="Monify API",
    description="Aplikasi Manajemen Keuangan - Backend",
    version="1.0.0"
)

allow_origins =[
    "http://127.0.0.1:5000",  # URL frontend lokal
    "kkp-dimas.vercel.app",  # ganti dengan domain frontend Anda
    "*",
]
# ───── Middleware CORS ─────
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,  # ganti dengan URL frontend jika ingin lebih aman
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ───── Event Startup ─────
@app.on_event("startup")
async def startup_event():
    print("📦 Membuat tabel database jika belum ada...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabel siap digunakan.")

# ───── Routing API ─────
app.include_router(calculator_router, prefix="/calculator", tags=["Calculator"])
app.include_router(dandur_router, prefix="/dandur", tags=["Dana Darurat"])
app.include_router(danpen_router, prefix="/danpen", tags=["Dana Pensiun"])
app.include_router(barangimpian_router, prefix="/barangimpian", tags=["Barang Impian"])
app.include_router(user_router, prefix="/auth", tags=["Authentication"])
app.include_router(transaction_router, prefix="/transactions", tags=["Transactions"])
app.include_router(category_router, prefix="/categories", tags=["Categories"])
app.include_router(analysis_router, prefix="/analysis", tags=["Analysis"])
app.include_router(metrics_router, include_in_schema=False)

# ───── Prometheus Instrumentation ─────
Instrumentator().instrument(app).expose(app)

# ───── Menjalankan Uvicorn secara langsung jika dijalankan sebagai skrip ─────
if __name__ == "__main__":
    import uvicorn
    if not os.getenv("DATABASE_URL"):
        print("❌ ERROR: DATABASE_URL tidak ditemukan di environment variable.")
        sys.exit(1)
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
