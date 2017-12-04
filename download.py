from tqdm import tqdm
from urllib.request import urlopen # Python 3

'''
import download
download.download_file_('https://g1.dcdn.lt/images/pix/siaures-koreja-76540773.jpg', 's')
'''
def iterate_file_chunks(url, chunk):
    response = urlopen(url)

    while True:
        data_chunk = response.read(chunk)
        if data_chunk:
            yield data_chunk
        else:
            break

def download_file(url, dst):
    site = urlopen(url)
    meta = site.info()
    total_size = int(meta.get("Content-Length"));

    CHUNK = 64 * 1024
    with open(dst, 'wb') as f:
        for data in tqdm(iterate_file_chunks(url, CHUNK), total=(total_size + (CHUNK-1)) // CHUNK, unit_scale=True):
            f.write(data)
