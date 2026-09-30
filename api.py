import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from chat import jawab

app = FastAPI(title="Chatbot Jiwanta")

# Saat website dan API berada di satu alamat (seperti setelah deploy),
# CORS tidak diperlukan. Izin "*" di bawah hanya untuk uji coba lokal
# (misalnya website dibuka lewat Live Server di port 5500).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Batas pemakaian, supaya API key OpenAI tidak terkuras pengunjung iseng.
BATAS_PER_MENIT = 8     # per alamat IP
BATAS_PER_HARI = 300    # total semua pengunjung
_antrean_ip = defaultdict(deque)
_total_hari = {"tanggal": "", "jumlah": 0}


def periksa_batas(request: Request):
    sekarang = time.time()
    forwarded = request.headers.get("x-forwarded-for")
    ip = forwarded.split(",")[-1].strip() if forwarded else request.client.host

    antrean = _antrean_ip[ip]
    while antrean and sekarang - antrean[0] > 60:
        antrean.popleft()
    if len(antrean) >= BATAS_PER_MENIT:
        raise HTTPException(status_code=429, detail="Terlalu banyak permintaan.")

    hari = time.strftime("%Y-%m-%d", time.gmtime(sekarang))
    if _total_hari["tanggal"] != hari:
        _total_hari["tanggal"], _total_hari["jumlah"] = hari, 0
    if _total_hari["jumlah"] >= BATAS_PER_HARI:
        raise HTTPException(status_code=429, detail="Kuota harian habis.")

    antrean.append(sekarang)
    _total_hari["jumlah"] += 1


class Pesan(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=1000)


class PermintaanChat(BaseModel):
    pertanyaan: str = Field(min_length=1, max_length=500)
    riwayat: list[Pesan] = Field(default_factory=list, max_length=20)


@app.get("/health")
def cek_status():
    return {"status": "ok", "layanan": "Chatbot Jiwanta"}


@app.post("/chat")
def chat(data: PermintaanChat, request: Request):
    periksa_batas(request)
    riwayat = [p.model_dump() for p in data.riwayat]
    return {"jawaban": jawab(data.pertanyaan, riwayat)}


# Sajikan website dari folder frontend. Harus paling akhir,
# supaya /chat dan /health tidak tertimpa.
FRONTEND = Path(__file__).parent / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")