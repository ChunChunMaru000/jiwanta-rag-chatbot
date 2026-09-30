import glob
import re

import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

load_dotenv()
client = OpenAI()

BATAS_PANJANG = 900
TUMPANG_TINDIH = 100
MODEL_EMBEDDING = "text-embedding-3-small"

# Baris judul: diawali nomor ("2. Daftar Menu") atau emoji kategori ("🥛 Milk Based")
POLA_JUDUL = re.compile(r"^(\d+\.\s|[\u2600-\u27BF\U0001F300-\U0001FAFF])")


def baca_pdf(path):
    reader = PdfReader(path)
    return "\n".join(halaman.extract_text() for halaman in reader.pages)


def pecah_per_bagian(teks):
    """Pisahkan teks menjadi bagian-bagian berdasarkan baris judul."""
    bagian = []
    judul, isi = "", []
    for baris in teks.splitlines():
        if POLA_JUDUL.match(baris.strip()):
            if isi:
                bagian.append((judul, "\n".join(isi).strip()))
            judul, isi = baris.strip(), []
        else:
            isi.append(baris)
    if isi:
        bagian.append((judul, "\n".join(isi).strip()))
    return bagian


def potong_panjang(judul, isi):
    """Bagian pendek dibiarkan utuh. Bagian panjang dipotong, judul ikut di tiap potongan."""
    if len(isi) + len(judul) <= BATAS_PANJANG:
        return [f"{judul}\n{isi}".strip()]
    hasil, mulai = [], 0
    while mulai < len(isi):
        akhir = min(mulai + BATAS_PANJANG, len(isi))
        if akhir < len(isi):
            batas = isi.rfind("\n", mulai, akhir)
            if batas > mulai + BATAS_PANJANG // 2:
                akhir = batas
        hasil.append(f"{judul}\n{isi[mulai:akhir].strip()}".strip())
        if akhir >= len(isi):
            break
        mulai = akhir - TUMPANG_TINDIH
    return hasil


def buat_potongan(teks):
    potongan = []
    for judul, isi in pecah_per_bagian(teks):
        if isi:
            potongan += potong_panjang(judul, isi)
    return potongan


def buat_embedding(daftar_teks):
    hasil = client.embeddings.create(model=MODEL_EMBEDDING, input=daftar_teks)
    return [item.embedding for item in hasil.data]


def main():
    path_pdf = glob.glob("data/*.pdf")[0]
    print("Membaca:", path_pdf)
    potongan = buat_potongan(baca_pdf(path_pdf))
    print("Jumlah potongan:", len(potongan))

    db = chromadb.PersistentClient(path="chroma_db")
    try:
        db.delete_collection("jiwanta")
    except Exception:
        pass  # belum ada koleksi lama, tidak apa-apa
    koleksi = db.create_collection("jiwanta")

    koleksi.add(
        ids=[f"potongan-{i}" for i in range(len(potongan))],
        documents=potongan,
        embeddings=buat_embedding(potongan),
    )
    print("Selesai. Data tersimpan di folder chroma_db")


if __name__ == "__main__":
    main()