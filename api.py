from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from chat import jawab

app = FastAPI(title="Chatbot Jiwanta")

# Izinkan website memanggil API ini dari browser.
# "*" berarti semua situs boleh (cukup untuk uji coba di laptop).
# Saat deploy, ganti dengan alamat websitemu yang sebenarnya.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class Pesan(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=1000)


class PermintaanChat(BaseModel):
    pertanyaan: str = Field(min_length=1, max_length=500)
    riwayat: list[Pesan] = Field(default_factory=list, max_length=20)


@app.get("/")
def cek_status():
    return {"status": "ok", "layanan": "Chatbot Jiwanta"}


@app.post("/chat")
def chat(data: PermintaanChat):
    riwayat = [p.model_dump() for p in data.riwayat]
    return {"jawaban": jawab(data.pertanyaan, riwayat)}