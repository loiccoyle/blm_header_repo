#!/usr/bin/env python3

import io
import zipfile
from pathlib import Path
from urllib.request import urlopen

URL = "https://github.com/loiccoyle/blm_header_repo/archive/master.zip"
KEEP_FOLDER = 'blm_header_repo-master/headers/'
DEST_FOLDER = Path('headers/')

if __name__ == "__main__":
    # download the zip
    file_data = urlopen(URL)
    data = file_data.read()
    # read from in memory zip
    zip_file = zipfile.ZipFile(io.BytesIO(data), "r")

    # prep destination folder
    if not DEST_FOLDER.is_dir():
        DEST_FOLDER.mkdir()

    # extract only the header files
    for z_file in zip_file.namelist():
        if z_file.startswith(KEEP_FOLDER) and z_file.endswith('.csv'):
            z_file = Path(z_file)
            with open(DEST_FOLDER / z_file.name, 'wb') as w_f:
                w_f.write(zip_file.read(str(z_file)))

