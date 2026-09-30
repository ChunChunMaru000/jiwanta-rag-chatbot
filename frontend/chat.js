// Widget chat Jiwanta: menampilkan tombol chat dan memanggil API chatbot.
(() => {
  // Saat uji di laptop, server berjalan di alamat ini.
  // Setelah deploy, ganti dengan alamat server online.
  const API_URL = "http://127.0.0.1:8000/chat";
  const MAKS_RIWAYAT = 12; // jumlah pesan terakhir yang dikirim ke server
  const PESAN_AWAL = "Halo! Ada yang bisa saya bantu?";

  const riwayat = [];
  let sedangMenunggu = false;

  function buatElemen(tag, kelas, teks) {
    const el = document.createElement(tag);
    if (kelas) el.className = kelas;
    if (teks) el.textContent = teks;
    return el;
  }

  // --- Susun tampilan ---
  const tombol = buatElemen("button", "jw-chat-btn", "💬");
  tombol.setAttribute("aria-label", "Buka chat");

  const panel = buatElemen("div", "jw-chat-panel");
  const kepala = buatElemen("div", "jw-chat-header");
  const judul = buatElemen("span", "jw-chat-title", "Jiwanta Café & Space");
  const tutup = buatElemen("button", "jw-chat-close", "✕");
  tutup.setAttribute("aria-label", "Tutup chat");
  kepala.append(judul, tutup);

  const daftarPesan = buatElemen("div", "jw-chat-messages");

  const form = buatElemen("form", "jw-chat-form");
  const input = buatElemen("input", "jw-chat-input");
  input.type = "text";
  input.placeholder = "Ketik pertanyaan Anda";
  input.maxLength = 500;
  input.autocomplete = "off";
  const kirimTombol = buatElemen("button", "jw-chat-send", "Kirim");
  kirimTombol.type = "submit";
  form.append(input, kirimTombol);

  panel.append(kepala, daftarPesan, form);
  document.body.append(tombol, panel);

  // --- Fungsi bantu ---
  function tambahPesan(pengirim, teks, sementara) {
    const el = buatElemen("div", `jw-msg ${pengirim}`);
    el.textContent = teks; // textContent mencegah kode berbahaya ikut dijalankan
    if (sementara) el.classList.add("typing");
    daftarPesan.append(el);
    daftarPesan.scrollTop = daftarPesan.scrollHeight;
    return el;
  }

  function aturPanel(buka) {
    panel.classList.toggle("open", buka);
    if (buka) input.focus();
  }

  async function kirim(pertanyaan) {
    tambahPesan("user", pertanyaan);
    const indikator = tambahPesan("bot", "Sedang mengetik...", true);
    sedangMenunggu = true;
    input.disabled = true;
    kirimTombol.disabled = true;

    try {
      const respons = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pertanyaan,
          riwayat: riwayat.slice(-MAKS_RIWAYAT),
        }),
      });
      if (!respons.ok) throw new Error("Status " + respons.status);
      const data = await respons.json();

      indikator.remove();
      tambahPesan("bot", data.jawaban);
      riwayat.push(
        { role: "user", content: pertanyaan },
        { role: "assistant", content: data.jawaban.slice(0, 1000) }
      );
    } catch (galat) {
      indikator.classList.remove("typing");
      indikator.textContent =
        "Maaf, chatbot sedang tidak bisa dihubungi. Silakan coba lagi sebentar lagi.";
    } finally {
      sedangMenunggu = false;
      input.disabled = false;
      kirimTombol.disabled = false;
      input.focus();
    }
  }

  // --- Pasang aksi ---
  tombol.addEventListener("click", () => aturPanel(!panel.classList.contains("open")));
  tutup.addEventListener("click", () => aturPanel(false));
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const pertanyaan = input.value.trim();
    if (!pertanyaan || sedangMenunggu) return;
    input.value = "";
    kirim(pertanyaan);
  });

  tambahPesan("bot", PESAN_AWAL);
})();