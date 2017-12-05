import urllib.request
from tqdm import tqdm
import os.path

def download_file(url, dst):
    if not os.path.isfile(dst):
        with urllib.request.urlopen(url) as response:
            total_size = int(response.info().get("Content-Length"))
            blocksize = 64 * 1024
            with tqdm(total=total_size, dynamic_ncols=True, unit='B', unit_scale=True) as pbar:
                with open(dst, 'wb') as f:
                    while True:
                        data = response.read(blocksize)
                        if data:
                            f.write(data)
                            pbar.update(len(data))
                        else:
                            break
    else :
        print ('File already downloaded (size: %d)' % os.path.getsize(dst))
