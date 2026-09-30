import glob

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

MODEL_EMBEDDING = "text-embedding-3-small"
MODEL_CHAT = "gpt-4o-mini"
JUMLAH_KONTEKS = 6
MAKS_RIWAYAT = 6  # jumlah pesan terakhir yang diingat (3 tanya + 3 jawab)

db = chromadb.PersistentClient(path="chroma_db")
koleksi = db.get_collection("jiwanta")

with open(glob.glob("prompts/*.txt")[0], encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()


def susun_ulang_pertanyaan(pertanyaan, riwayat):
    """Ubah pertanyaan lanjutan jadi pertanyaan lengkap agar pencarian akurat."""
    if not riwayat:
        return pertanyaan
    percakapan = "\n".join(f"{p['role']}: {p['content']}" for p in riwayat)
    hasil = client.chat.completions.create(
        model=MODEL_CHAT,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "Tulis ulang pertanyaan terakhir pelanggan menjadi satu "
                    "pertanyaan lengkap yang bisa dipahami tanpa membaca "
                    "percakapan sebelumnya. Jika sudah lengkap, tulis apa "
                    "adanya. Jawab hanya dengan pertanyaannya."
                ),
            },
            {
                "role": "user",
                "content": f"Percakapan sebelumnya:\n{percakapan}\n\nPertanyaan terakhir: {pertanyaan}",
            },
        ],
    )
    return hasil.choices[0].message.content.strip()


def cari_konteks(pertanyaan):
    embedding = client.embeddings.create(
        model=MODEL_EMBEDDING, input=[pertanyaan]
    ).data[0].embedding
    hasil = koleksi.query(query_embeddings=[embedding], n_results=JUMLAH_KONTEKS)
    return hasil["documents"][0]


def jawab(pertanyaan, riwayat=None):
    riwayat = (riwayat or [])[-MAKS_RIWAYAT:]
    pertanyaan_lengkap = susun_ulang_pertanyaan(pertanyaan, riwayat)
    konteks = "\n\n---\n\n".join(cari_konteks(pertanyaan_lengkap))

    pesan = [{"role": "system", "content": SYSTEM_PROMPT + "\n\nKonteks:\n" + konteks}]
    pesan += riwayat
    pesan.append({"role": "user", "content": pertanyaan})

    hasil = client.chat.completions.create(
        model=MODEL_CHAT, messages=pesan, temperature=0.3
    )
    return hasil.choices[0].message.content


if __name__ == "__main__":
    print("Chatbot Jiwanta siap. Ketik 'keluar' untuk berhenti.")
    riwayat = []
    while True:
        tanya = input("\nKamu: ").strip()
        if tanya.lower() in ("keluar", "exit", "quit"):
            break
        if not tanya:
            continue
        jawaban = jawab(tanya, riwayat)
        print("Bot:", jawaban)
        riwayat.append({"role": "user", "content": tanya})
        riwayat.append({"role": "assistant", "content": jawaban})