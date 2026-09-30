import re
import subprocess
from urllib.parse import unquote

HTML = "frontend/index.html"

with open(HTML, encoding="utf-8") as f:
    isi = f.read()

# Semua jalur lokal yang dipakai src="..." di index.html
dipakai = sorted(set(re.findall(r'src="(?!https?://|//|data:)([^"]+)"', isi)))

# Semua file yang benar-benar dilacak Git (persis seperti yang akan di-deploy)
keluaran = subprocess.check_output(["git", "ls-files", "-z"])
dilacak = set(keluaran.decode("utf-8").split("\0"))
dilacak_kecil = {p.lower() for p in dilacak}

masalah = 0
for jalur in dipakai:
    lengkap = "frontend/" + unquote(jalur).lstrip("/")
    if lengkap in dilacak:
        continue
    masalah += 1
    if lengkap.lower() in dilacak_kecil:
        print("BESAR-KECIL HURUF BEDA:", jalur)
    else:
        print("TIDAK ADA DI GIT:      ", jalur)

print(f"\nDiperiksa {len(dipakai)} gambar, bermasalah {masalah}.")