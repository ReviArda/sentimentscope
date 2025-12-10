import urllib.request
import urllib.error
import os
import mimetypes
import uuid

url = 'http://127.0.0.1:5000/api/upload-train-data'
file_path = 'dummy_train.csv'

if not os.path.exists(file_path):
    print(f"Error: {file_path} not found.")
    exit(1)

# Helper to create multipart/form-data body
def encode_multipart_formdata(fields, files):
    boundary = uuid.uuid4().hex.encode('utf-8')
    body = b''

    for key, value in fields.items():
        body += b'--' + boundary + b'\r\n'
        body += f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode('utf-8')
        body += value.encode('utf-8') + b'\r\n'

    for key, (filename, content) in files.items():
        body += b'--' + boundary + b'\r\n'
        body += f'Content-Disposition: form-data; name="{key}"; filename="{filename}"\r\n'.encode('utf-8')
        body += b'Content-Type: text/csv\r\n\r\n'
        body += content + b'\r\n'

    body += b'--' + boundary + b'--\r\n'
    content_type = f'multipart/form-data; boundary={boundary.decode("utf-8")}'
    return body, content_type

try:
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    body, content_type = encode_multipart_formdata({}, {'file': ('dummy_train.csv', file_content)})
    
    req = urllib.request.Request(url, data=body, headers={'Content-Type': content_type})
    print(f"Uploading {file_path} to {url}...")
    
    with urllib.request.urlopen(req) as response:
        print(f"Status Code: {response.status}")
        print(f"Response: {response.read().decode('utf-8')}")
        print("✅ Upload successful! Training should be running in background.")

except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.reason}")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")
