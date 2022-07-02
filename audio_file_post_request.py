
import requests
import base64


def get_file_data(path_to_file):

    with open (path_to_file , 'rb') as file :
        filename = file.name
        data = base64.b64encode(file.read())
        return filename , data
    
filename , data = get_file_data('test_sound.wav')

url = 'http://127.0.0.1:5000/transcription'
payload = {
    'filename' : filename , 
    'data' : data.decode("utf-8")
}
headers= {
    'Content-Type' : 'application/json'
}

r= requests.post(url , json = payload , headers = headers )
print(r.text)