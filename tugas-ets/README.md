# Tugas ETS

### Detail Tugas

Mengimplementasikan kode program untuk server dari contoh referensi yang diberikan dengan ketentuan berikut:

- [Multithreading](https://github.com/vitoananta3/progjar-2024/blob/main/tugas-ets/server-thread-http.py)
- [Multiprocessing](https://github.com/vitoananta3/progjar-2024/blob/main/tugas-ets/server-process-http.py)
- [Multithreading (secure)](https://github.com/vitoananta3/progjar-2024/blob/main/tugas-ets/server-thread-http-secure.py)
- [Multiprocessing (secure)](https://github.com/vitoananta3/progjar-2024/blob/main/tugas-ets/server-process-http-secure.py)


### Cara Menjalankan

1. Clone repository

    ```
    git clone https://github.com/vitoananta3/progjar-2024.git
    ```

2. Pindah ke directory hasil dari clone tersebut

    ```
    cd progjar-2024
    ```

3. Pindah ke directory hasil dari clone tersebut

    ```
    cd tugas-ets
    ```

4. Jalankan environment masing-masing

5. Jalankan server yang diinginkan, contoh menjalankan multithreading http secure server:

    ```
    python3 server-thread-http-secure.py
    ```

6. Install package untuk melakukan benchmark, dalam hal ini saya menggunakan siege:

    ```
    sudo apt update
    ```

    ```
    sudo apt install siege -y
    ```

7. Lakukan benchmark, contoh menjalankan benchmark dengan jumlah request 1000 dengan concurrency 50

    ```
    siege -c50 -r20 https://[IP mesin server]:[port server]/
    ```

### Contoh hasil benchmark
![Contoh hasil benchmark](https://github.com/vitoananta3/progjar-2024/blob/main/assets/tugas-ets/thread-https/hasil-thread-https-50.png)
