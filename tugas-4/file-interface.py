import os
import json
import base64
from glob import glob


class FileInterface:
    def __init__(self):
        os.chdir('files/')

    def list(self,params=[]):
        try:
            filelist = glob('*.*')
            return dict(status='OK', data=filelist)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def get(self, params=[]):
        try:
            filename = params[0]
            if (filename == ''):
                return dict(status='ERROR', data='file yang ingin diambil kosong')
            if not os.path.isfile(filename):
                return dict(status='ERROR', data='file yang ingin diambil tidak ada')
            fp = open(f"{filename}",'rb')
            isi_file = base64.b64encode(fp.read()).decode()
            return dict(status='OK',data_namafile=filename, data_file=isi_file, data_pesan='telah diambil')
        except Exception as e:
            return dict(status='ERROR',data=str(e))

    def upload(self, params=[]):
        try:
            total_params = len(params)
            # print(f"total params: {total_params}")
            if total_params < 2:
                return dict(status='ERROR', data='untuk upload file diperlukan 2 parameter: "nama_file konten_file"')
            filename = params[0]
            file_content = params[1]
            if not filename:
                return dict(status='ERROR', data='file yang ingin diupload kosong')
            if not file_content:
                return dict(status='ERROR', data='konten file yang ingin diupload kosong')
            file_data = base64.b64decode(file_content)
            with open(filename, 'wb') as fp:
                fp.write(file_data)
            return dict(status='OK', data_pesan='telah diupload')
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def delete(self, params=[]):
        try:
            filename = params[0]
            if not filename:
                return dict(status='ERROR', data='file yang ingin dihapus kosong')
            if not os.path.isfile(filename):
                return dict(status='ERROR', data='file yang ingin dihapus tidak ada')
            os.remove(filename)
            return dict(status='OK', data_pesan='telah dihapus')
        except Exception as e:
            return dict(status='ERROR', data=str(e))

if __name__=='__main__':
    f = FileInterface()
    #contoh pemakaian
    # print(f.list())
    # print(f.get(['pokijan.jpg']))
    # print(f.get(['']))
    # print(f.get(['gagal-get.txt']))
    # print(f.upload(['musuh-donal-bebek.txt', base64.b64encode(b'pojikan, gerombolan siberat, untung angasa, mimi hitam').decode()]))
    # print(f.upload(['']))
    # print(f.upload(['nama-file-saja.txt', '']))
    # print(f.upload(['', base64.b64encode(b'konten file saja').decode()]))
    # print(f.delete(['musuh-donal-bebek.txt']))
    # print(f.delete(['']))
    # print(f.delete(['gagal-hapus.png']))


