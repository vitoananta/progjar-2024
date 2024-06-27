# Tugas 5

### Detail Tugas

Impelementasikan load balancer dengan mode ansynchronous dan mode server thread, lalu lakukan test serta berikan kesimpulannya. Referensi [progjar4a](https://github.com/rm77/progjar/tree/master/progjar6)

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
   cd tugas-5
   ```

4. Jalankan environment masing-masing

Untuk mode async:

1. Jalankan runserver.sh

   ```
   bash runserver.sh
   ```

2. Jalankan lb_async.py

   ```
   python3 lb_async.py 55555
   ```

3. Jalankan test dengan wrk dengan n adalah parameter concurrency

   ```
   wrk -c 1000 -t {n} http://url
   ```

Untuk mode server thread:

1. Jalankan runserver.sh

   ```
   bash runserver_2.sh
   ```

2. Jalankan lb_async.py

   ```
   python3 lb_process.py
   ```

3. Jalankan test dengan wrk dengan n adalah parameter concurrency

   ```
   wrk -c 1000 -t {n} http://url
   ```
