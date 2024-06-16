# Tugas 4

### Detail Tugas

Tambahkan operasi UPLOAD dan DELETE pada protokol file server. Referensi [progjar4a](https://github.com/rm77/progjar/tree/master/progjar4a)

### Cara Menjalankan

1. Clone repository

   ```
   git clone https://github.com/vitoananta3/progjar-2024.git
   ```

2. Pindah ke directory hasil dari clone tersebut

   ```
   cd progjar-2024
   ```

3. Pindah ke directory tugas 2

   ```
   cd tugas-4
   ```

4. Jalankan environment masing-masing

5. Jalankan file_server.py

   ```
   python file_server.py
   ```

6. Jalankan file_client.py

   ```
   python file_client.py
   ```

### Update Spesifikasi Protokol

[Dokumen Spesifikasi Protokol](https://github.com/vitoananta/progjar-2024/blob/main/tugas-4/PROTOKOL.txt)

https://github.com/vitoananta/progjar-2024/blob/ff18052ea829da79a278bec40a9952e2a4ab1371/tugas-4/PROTOKOL.txt#L1-L76

https://github.com/vitoananta/progjar-2024/blob/ff18052ea829da79a278bec40a9952e2a4ab1371/tugas-4/PROTOKOL.txt#L79-L86


### Penjelasan Spesifikasi Protokol Baru

- UPLOAD

Pada permintaan UPLOAD, proses dimulai dari file file_client.py yang memanggil fungsi remote_upload. Fungsi ini membaca file lokal yang akan diunggah, mengubah/men-encode isinya menjadi string base64, dan membentuk perintah UPLOAD. Perintah ini dikirim ke server melalui jaringan dengan berbagai potongan/chunks yang akan ditahan sampai selesai dengan tanda “"\r\n\r\n". Di sisi server, file_server.py menerima koneksi dari client dan memanggil kelas ProcessTheClient untuk menangani komunikasi. Data perintah yang diterima akan diteruskan ke FileProtocol untuk diproses oleh metode proses_string. Di dalam metode ini, file_protocol.py memeriksa perintah, mendekode konten file dari string base64, dan menyimpannya sebagai file baru di direktori server melalui metode upload pada kelas FileInterface di file_interface.py. Jika proses berhasil, server mengirimkan respon status "OK" kembali ke client. Jika gagal, server mengirimkan respon status "ERROR" beserta pesan kesalahan yang sesuai.


- DELETE


Pada permintaan DELETE, proses dimulai dari file file_client.py yang memanggil fungsi remote_delete. Fungsi ini membentuk perintah DELETE dengan menyertakan nama file yang akan dihapus dan mengirimkannya ke server melalui jaringan. Di sisi server, file_server.py menerima koneksi dari client dan memanggil kelas ProcessTheClient untuk menangani komunikasi. Data perintah yang diterima akan diteruskan ke FileProtocol untuk diproses oleh metode proses_string. Di dalam metode ini, file_protocol.py memeriksa perintah dan memanggil metode delete pada kelas FileInterface di file_interface.py. Metode delete memeriksa apakah file yang dimaksud ada di direktori server dan jika ada, file tersebut dihapus. Jika proses berhasil, server mengirimkan respon status "OK" kembali ke client. Jika gagal, server mengirimkan respon status "ERROR" beserta pesan kesalahan yang sesuai.


### Hasil Operasi (Sebelum vs Sesudah Operasi Dijalankan)

- Sebelum

![](https://github.com/vitoananta/progjar-2024/blob/main/assets/tugas-4/sebelum-dijalankan-operasi-baru.png)

- Sesudah

![](https://github.com/vitoananta/progjar-2024/blob/main/assets/tugas-4/setelah-dijalankan-operasi-baru.png)


### Video Demo Operasi Baru Dijalankan

https://github.com/vitoananta/progjar-2024/assets/142609964/e034f82f-232e-4ba9-8c2e-63f5dad65196
