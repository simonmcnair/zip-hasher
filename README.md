This recursively scans a directory creating hashes for all files.  This includes within zip files.  It will also create the hash from the audio or image data itself, rather than the file so that small changes in metadata do not hide the same file.



Requirements :
  create a venv
  /venv/bin/pip install -r requirements.txt

Instructions : 
  1. run `python main.py -z path/to/hash`
  
