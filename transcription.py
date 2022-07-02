import base64 , datetime
from flask import Flask, request
from transcription_service import start_transcription


app = Flask(__name__)
#app.debug = True

@app.route('/transcription', methods=['POST'])
def transcription_():

    file = request.get_json()
    with open ('tempdir/{}'.format(file['filename']), 'wb') as f :
        decoded_string = base64.b64decode(file['data'].encode("utf-8"))
        f.write(decoded_string)

    unique_id = datetime.datetime.now().strftime("%I%M%p%S")
    speakers=start_transcription('tempdir/'+file['filename'],unique_id)
    
    
        

    return {'speaker_1' : speakers[0],
            'speaker_2' : speakers[1] }


if __name__ == "__main__":
    
    app.run(host="127.0.0.1", port=5000)