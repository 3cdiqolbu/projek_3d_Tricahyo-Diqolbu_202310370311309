# 3D Rocket Model with Python and Plotly

Proyek ini mendemonstrasikan pembuatan model roket 3D menggunakan primitif 3D dasar, transformasi geometris, dan scene graph sederhana, semuanya dirender di browser web menggunakan Python (Pyodide) dan Plotly.

## Deskripsi Model

Model roket 3D ini terdiri dari komposisi berbagai objek 3D dasar:

* **Badan Roket:** Direpresentasikan oleh **silinder (cylinder)**.
* **Kerucut Hidung (Nose Cone):** Direpresentasikan oleh **kerucut (cone)**.
* **Sirip (Fins - 3x):** Masing-masing sirip direpresentasikan oleh **kubus (cube)** yang diubah skalanya dan diposisikan menyerupai sirip roket.
* **Jendela (Windows - 3x):** Direpresentasikan oleh **bola (sphere)**.
* **Knalpot Mesin (Exhaust):** Direpresentasikan oleh **silinder (cylinder)** yang lebih pendek dan lebar di bagian bawah roket.
* **Nozel Mesin (Nozzles - 2x):** Direpresentasikan oleh **kerucut (cone)** yang lebih kecil dan terbalik di dalam knalpot.
* **Cincin Hiasan (Decorative Rings - 2x):** Direpresentasikan oleh **torus (torus)** di bagian atas dan bawah badan roket.

## Komposisi dan Transformasi

Model ini dibangun menggunakan scene graph sederhana di mana "roket" bertindak sebagai grup utama, dan semua komponennya (badan, kerucut hidung, sirip, jendela, knalpot, nozel, cincin) adalah objek primitif individual. Setiap primitif mengalami transformasi spesifik:

1.  **Badan Roket (Silinder):**
    * **Ukuran Awal:** `radius=1.0`, `height=6.0`
    * **Translasi:** `[0, 0, 3.0]` - Ditempatkan agar bagian tengah silinder berada pada `Z=3.0`, sehingga dasar roket berada di `Z=0`.

2.  **Kerucut Hidung (Kerucut):**
    * **Ukuran Awal:** `radius=1.0`, `height=3.0`
    * **Translasi:** `[0, 0, 6.0]` - Ditempatkan di atas badan roket, sehingga dasarnya menyatu dengan bagian atas badan.

3.  **Sirip (Kubus - 3 instance):**
    * **Ukuran Awal:** `[0.2, 2.5, 2.0]` (Tebal, Panjang, Tinggi)
    * **Translasi:** `[0, -1.0, 1.0]` - Posisi dasar setiap sirip relatif terhadap badan roket.
    * **Rotasi Z:** `[0]`, `[120]`, `[240]` - Diputar mengelilingi sumbu Z untuk menempatkan sirip secara merata di sekitar badan roket.
    * **Rotasi X:** `[10]` - Sedikit dimiringkan ke atas untuk memberikan tampilan yang lebih dinamis.

4.  **Jendela (Bola - 3 instance):**
    * **Ukuran Awal:** `radius=0.3`
    * **Translasi:** Ditempatkan di sekitar badan roket pada ketinggian yang berbeda, dengan `x` dan `y` yang dihitung untuk melingkari badan. Contoh: `[0.8, 0, 5.0]` untuk jendela pertama.

5.  **Knalpot Mesin (Silinder):**
    * **Ukuran Awal:** `radius=0.7`, `height=1.0`
    * **Translasi:** `[0, 0, -0.5]` - Ditempatkan di bawah dasar badan roket.

6.  **Nozel Mesin (Kerucut - 2 instance):**
    * **Ukuran Awal:** `radius=0.3`, `height=0.8`
    * **Translasi:** Ditempatkan di dalam knalpot, sedikit terpisah. Contoh: `[0.3, 0.3, -0.9]`.
    * **Rotasi X:** `[180]` - Diputar agar ujung kerucut mengarah ke bawah, menyerupai nosel pendorong.

7.  **Cincin Hiasan (Torus - 2 instance):**
    * **Ukuran Awal:** `major_radius=1.1`, `minor_radius=0.05`
    * **Translasi:** `[0, 0, 5.5]` untuk cincin atas (dekat sambungan kerucut hidung) dan `[0, 0, 1.5]` untuk cincin bawah.

## Struktur Scene Graph

`scene_graph` di `main.py` adalah kamus yang mendefinisikan struktur hirarkis roket. Ini memiliki grup "roket" tingkat atas, yang berisi daftar "anak-anak"nya (badan, kerucut hidung, sirip, jendela, knalpot, nozel, cincin). Setiap anak adalah "primitif" dengan `shape`, `color`, `initial_radius`/`height`/`size` (tergantung bentuk), dan daftar `transformations` untuk diterapkan.

## Cara Menjalankan

1.  **Unduh:** Unduh seluruh folder `projek_3d_roket_nama_nim/` (pastikan berisi `index.html`, `main.py`, dan `README.md`).
2.  **Buka `index.html`:** Cukup buka file `index.html` di browser web Anda.
3.  **Tunggu Memuat:** Halaman akan memuat lingkungan Pyodide dan menjalankan skrip Python. Ini mungkin memerlukan beberapa saat tergantung koneksi internet Anda.
4.  **Lihat Model:** Setelah dimuat, model roket 3D akan ditampilkan di browser. Anda dapat berinteraksi dengannya (memutar, memperbesar/memperkecil) menggunakan mouse Anda.

## Menjalankan di itch.io

Untuk menjalankan proyek ini di itch.io:

1.  **Kompres Folder:** Kompres folder `projek_3d_roket_nama_nim/` menjadi file `.zip`. Pastikan `index.html` berada di direktori akar ZIP.
2.  **Buat Proyek Baru:** Buka dasbor itch.io Anda dan buat proyek baru.
3.  **Unggah File:** Di bagian "Uploads", unggah file `.zip` Anda.
4.  **Konfigurasi Tipe Proyek:** Atur "Kind of project" ke "HTML".
5.  **Enable Fullscreen (Opsional):** Centang "Enable Fullscreen button" untuk pengalaman melihat yang lebih baik.
6.  **Save & View:** Simpan proyek Anda, dan kemudian Anda dapat melihatnya langsung di browser Anda di itch.io.
