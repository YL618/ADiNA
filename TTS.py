import threading
import time
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from google.cloud import texttospeech
import logging
import os
import soundfile as sf
from socket import *

# setup logging , format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './new_google.json'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger().setLevel(logging.DEBUG)

class UnityConnection(threading.Thread):
    def __init__(self,general_logger):
        logging.info("Initializing UnityConnection")
        super().__init__()
        self.ip = ""
        self.port =8030
        self.general_logger=general_logger

    def run(self):
        global send_data_byte
        global global_play
        global global_text
        global global_connect
        global global_filler
        global global_filler_en
        global unitystop
        global adina_mood
        logging.info("Before socket")
        server = socket(AF_INET, SOCK_STREAM)
        server.bind((self.ip, self.port))
        logging.info("waiting for connection")
        server.listen(5)
        connection, addr = server.accept()
        logging.info(f"[*]Connect to the client {addr[0]}:{addr[1]}")
        # global_connect = False
        global_connect = True

        while True:
            try:
                # If project close, then try to reconnect
                if( global_connect == False):
                    print("strat reconnect")
                    logging.info("waiting for connection")
                    server.listen(5)
                    connection, addr = server.accept()
                    logging.info(f"[*]Connect to the client {addr[0]}:{addr[1]}")
                    global_connect = True


                while (global_play == False):
                    if (global_connect == False):
                        print("reconnect")
                        logging.info("waiting for connection")
                        server.listen(5)
                        connection, addr = server.accept()
                        logging.info(f"[*]Connect to the client {addr[0]}:{addr[1]}")
                        global_connect = True
                    pass
                logging.info("exit the loop")

                if global_filler:
                    if global_filler_en:
                        #global_filler=False

                        #global_play = False
                        logging.info("sending filler")
                        message = 'filler'
                        connection.send(message.encode())
                    else:
                        #global_filler = False
                        # global_connect = False
                        #global_play = False
                        logging.info("sending fillerfr")
                        message = 'fillfr'
                        connection.send(message.encode())
                else:
                    logging.info("enter here")
                    logging.info(global_text)
                    #output = self.google_output(global_text)
                    #send_data_byte = g_output.tobytes()
                    message = 'replys'
                    connection.send(message.encode())


                    if (adina_mood=='joyful'):
                        message = 'joyful'

                    elif (adina_mood=='worried'):
                        message = 'worryy'

                    else:
                        message = 'neutrl'


                    connection.send(message.encode())
                    logging.info("mood message sent")
                    wav_length = len(send_data_byte)
                    #client_socket.send(struct.pack('!I', wav_length))  # Pack as network (big-endian) order

                    logging.info("logging.info(wav_length)")
                    logging.info(wav_length)
                    start=time.time()
                    connection.send(send_data_byte)
                    elaspedtime = time.time() - start
                    print("sendingtime"+str(elaspedtime))
                    # global_connect = False
                    logging.info("message sent")
                    inmood = "neutral"
                    #global_play = False

                global_filler = False
                global_play = False


            # except:
            #     global_connect = False
            #     #unitystop == False
            #     print("here reconnect")
            #     logging.info("waiting for connection")
            #     server.listen(5)
            #     connection, addr = server.accept()
            #     logging.info(f"[*]Connect to the client {addr[0]}:{addr[1]}")
            #     global_connect = True
            except ConnectionRefusedError:
                print("Connection refused. The server is not running or unavailable.")
            except ConnectionError as e:
                print(f"Connection error: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")

# Following are the global values that will be used in running
#what text we want to render
global_text = ""
#if we want to send a sentence to play
global_play=False
#if TCP is working well
global_connect=False
#whether to trigger the filler
global_filler=False
#if unity is stopped
unitystop=True
#scaler controlling return with a time delay
audio_length=2
#adina's mood
adina_mood="neutral"

#Debug logger
logger=logging.getLogger().setLevel(logging.INFO)
thread=UnityConnection(logger)

# Start the thread
thread.start()
print("thread start")
logging.info("thread start")

app = Flask(__name__)

def google_output(input_text,IsEn):
    global send_data_byte
    global audio_length
    logging.info("google_output(input_text)")
    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=input_text)

    if IsEn:

        # Build the voice request, select the language code ("en-US") and the ssml
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", name="en-US-Neural2-F", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
    else:
        voice = texttospeech.VoiceSelectionParams(
            language_code="fr-CA", name="fr-CA-Neural2-A", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    # The response's audio_content is binary.
    with open("output.wav", "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)

    return "finish"

@app.route('/tts', methods=['POST'])
@cross_origin()
def tts():
    global send_data_byte
    global global_play
    global global_text
    global global_connect
    global audio_length
    global adina_mood

    data = request.get_json()
    intext=data.get('text')
    inmood = data.get('mood')
    adina_mood=inmood

    logging.info("inmood=")
    logging.info(inmood)

    if intext:
        if global_connect==False:
            logging.info("global_connect=False")
            #global_play = True
            return "global_connect=False"
        else:
            logging.info("text receive")
            global_text=intext
            IsEn = True
            start=time.time()
            status=google_output(intext,IsEn)
            elaspedtime=time.time()-start
            print("GoogleTTStime"+str(elaspedtime))
            start = time.time()
            data, fs = sf.read('output.wav', dtype='float32')
            elaspedtime = time.time() - start
            print("Savingtime" + str(elaspedtime))

            send_data_byte = data.tobytes()
            global_play = True
            if global_play:
                logging.info("global_play=True")
            duration = len(data) / float(fs)
            rounded = round(duration, 1)
            audio_length = rounded
            logging.info("in flask, audio_length=")
            logging.info(audio_length)
            time.sleep(audio_length*1.24)

            #now returns a value to client so it knows that the graphic rendering has finished
            return "finished playing", 200
    else:
        return 'Text input is missing', 400


@app.route('/ttsfr', methods=['POST'])
@cross_origin()
def ttsfr():
    global send_data_byte
    global global_play
    global global_text
    global global_connect
    global audio_length
    global adina_mood

    data = request.get_json()
    intext = data.get('text')
    inmood = data.get('mood')
    adina_mood = inmood
    logging.info("inmood=")
    logging.info(inmood)

    if intext:
        if global_connect==False:
            logging.info("global_connect=False")
            #global_play = True
            return "global_connect=False"
        else:

            logging.info("text receive")
            global_text=intext
            IsEn=False
            status=google_output(intext,IsEn)
            data, fs = sf.read('output.wav', dtype='float32')
            send_data_byte = data.tobytes()
            global_play = True
            if global_play:
                logging.info("global_play=True")
            duration = len(data) / float(fs)
            rounded = round(duration, 1)
            audio_length = rounded
            logging.info("in flask, audio_length=")
            logging.info(audio_length)
            time.sleep(audio_length*1.24)

            #now returns a value to client so it knows that the graphic rendering has finished
            return "finished playing", 200
    else:
        return 'Text input is missing', 400

#  THIS WILL BE CALLED BY THE CLIENT AS SOON AS THE USER AUDIO HAS BEEN CAPTURED

@app.route('/filler')
@cross_origin()
def filler():
    logging.info("filler enter")
    global global_play
    global global_connect
    global global_filler
    global global_filler_en

    if global_connect == False:
        logging.info("global_connect=False")
        #global_play = True
        return "global_connect=False"
    else:
        logging.info("filler start")
        global_filler = True
        global_play = True
        global_filler_en = True
    return "filler playing", 200


@app.route('/fillerfr')
@cross_origin()
def fillerfr():
    logging.info("filler fr enter")
    global global_play
    global global_connect
    global global_filler
    global global_filler_en

    if global_connect == False:
        logging.info("global_connect=False")
        #global_play = True
        return "global_connect=False"
    else:
        logging.info("filler start")
        global_filler = True
        global_play = True
        global_filler_en=False
    return "filler playing", 200

@app.route('/unitystart')
@cross_origin()
def unitystart():
    global global_connect
    #global unitystop
    logging.info("unitystart")
    #unitystop = False
    global_connect=True
    return "unitystart", 200

@app.route('/unityclose')
@cross_origin()
def unityclose():
    global global_connect
    #global unitystop
    logging.info("unityclose")
    #unitystop = True
    global_connect=False
    return "unityclose", 200

if __name__ == '__main__':
    # Start the TCP connection
    app.run(debug=True,host='0.0.0.0', port=4100)
    logging.info("app.run")








