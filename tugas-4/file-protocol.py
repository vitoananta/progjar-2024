import json
import logging
import shlex
import base64

from file_interface import FileInterface

"""
* class FileProtocol bertugas untuk memproses 
data yang masuk, dan menerjemahkannya apakah sesuai dengan
protokol/aturan yang dibuat

* data yang masuk dari client adalah dalam bentuk bytes yang 
pada akhirnya akan diproses dalam bentuk string

* class FileProtocol akan memproses data yang masuk dalam bentuk
string
"""

class FileProtocol:
    def __init__(self):
        self.file = FileInterface()
    def proses_string(self, string_datamasuk=''):
        logging.warning(f"string diproses: {string_datamasuk}")
        try:
            if string_datamasuk.lower().startswith("upload"):
                bagian = string_datamasuk.split(maxsplit=2)
                if len(bagian) < 3:
                    return json.dumps(dict(status='ERROR', data='untuk upload file diperlukan 2 parameter: "nama_file konten_file"'))
                c_request = bagian[0].strip().lower()
                filename = bagian[1].strip()
                file_content = bagian[2].strip()
                params = [filename, file_content]
            else:
                c = shlex.split(string_datamasuk.lower())
                c_request = c[0].strip()
                params = [x for x in c[1:]] if len(c) > 1 else ['']

            logging.warning(f"memproses request: {c_request}")
            cl = getattr(self.file, c_request)(params)
            return json.dumps(cl)
        except Exception:
            return json.dumps(dict(status='ERROR',data='request tidak dikenali'))


if __name__=='__main__':
    fp = FileProtocol()
    konten_file_test_base64 = base64.b64encode(b'pojikan, gerombolan siberat, untung angasa, mimi hitam').decode()
    #contoh pemakaian
    # print(f"konten file: {konten_file_test_base64}")
    # print(fp.proses_string("LIST"))
    # print(fp.proses_string("GET pokijan.jpg"))
    # print(fp.proses_string("GET"))
    # print(fp.proses_string("GET gagal-get.txt"))
    # print(fp.proses_string(f"UPLOAD musuh-donal-bebek.txt {konten_file_test_base64}"))
    # print(fp.proses_string("UPLOAD"))
    # print(fp.proses_string("UPLOAD nama-file-saja.txt "))
    # print(fp.proses_string(f"UPLOAD {konten_file_test_base64}"))
    # print(fp.proses_string(f"DELETE musuh-donal-bebek.txt"))
    # print(fp.proses_string(f"DELETE"))
    # print(fp.proses_string(f"DELETE gagal-hapus.png"))

