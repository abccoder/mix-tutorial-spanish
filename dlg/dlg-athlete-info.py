#!/opt/rh/rh-python36/root/usr/bin/python
from re import I, U
import pyaudio
import wave
import click

import argparse
import logging
import os
import sys
import datetime
import time
import requests
import simpleaudio as sa

from pytz import timezone

from google.protobuf.json_format import MessageToJson, MessageToDict
from google.protobuf.struct_pb2 import Struct

from grpc import StatusCode
from nuance.dlg.v1.common.dlg_common_messages_pb2 import *
from nuance.dlg.v1.dlg_messages_pb2 import *
from nuance.dlg.v1.dlg_interface_pb2 import *
from nuance.dlg.v1.dlg_interface_pb2_grpc import *

from sportinf import SportInfo

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def getAuthToken():
    client_id="<client_id>"
    secret="<secret>"

    base_url = 'https://auth.crt.nuance.com'
    grant_type='client_credentials'

    response = requests.post(base_url+'/oauth2/token',
                             auth=(client_id, secret),
                             data={'grant_type':grant_type,
                                   'scope':'dlg',
                                   'token_endpoint_auth_method':'client_secret_post'})
    
    token = response.json()["access_token"]
    return token

# Generates the .wav file header for a given set of parameters
def genHeader(sampleRate, bitsPerSample, channels, datasize, formattype):
    o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE",'ascii')                                              # (4byte) File type
    o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
    o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
    o += (formattype).to_bytes(2,'little')                                  # (2byte) Format type (1 - PCM)
    o += (channels).to_bytes(2,'little')                                    # (2byte) Will always be 1 for TTS
    o += (sampleRate).to_bytes(4,'little')                                  # (4byte) 
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
    o += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
    o += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
    o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
    return o

# On windows, records an audio file using pyaudio for demo purposes
# http://people.csail.mit.edu/hubert/pyaudio/#record-example

def record_audio(user_audio):
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 1
    fs = 16000  # Record at 16000 samples per second
    seconds = 6
    
    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    click.secho('Recording..', fg='red')

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []  # Initialize array to store frames

    # Store data in chunks for 6 seconds
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream 
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()

    click.secho('..Finished recording.', fg='red')

    # Save the recorded data as a WAV file
    wf = wave.open(user_audio, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

def create_channel(args):
    token = getAuthToken()
    log.debug("Adding CallCredentials with token %s" % token)
    call_credentials = grpc.access_token_call_credentials(token)

    log.debug("Creating secure gRPC channel")
    channel_credentials = grpc.ssl_channel_credentials()
    channel_credentials = grpc.composite_channel_credentials(channel_credentials, call_credentials)
    channel = grpc.secure_channel(args.serverUrl, credentials=channel_credentials)

    return channel

def start_request(stub, model_ref_dict, session_id, selector_dict={}):
    selector = Selector(channel=selector_dict.get('channel'), 
                        library=selector_dict.get('library'),
                        language=selector_dict.get('language'))
    start_payload = StartRequestPayload(model_ref=model_ref_dict)
    start_req = StartRequest(session_id=session_id, 
                        selector=selector, 
                        payload=start_payload)
    log.debug(f'Start Request: {start_req}')
    start_response, call = stub.Start.with_call(start_req)
    response = MessageToDict(start_response)
    log.debug(f'Start Request Response: {response}')
    return response, call

def parse_args():
    parser = argparse.ArgumentParser(
        prog="dlg_client.py",
        usage="%(prog)s [-options]",
        add_help=False,
        formatter_class=lambda prog: argparse.HelpFormatter(
            prog, max_help_position=45, width=100)
    )

    options = parser.add_argument_group("options")
    options.add_argument("-h", "--help", action="help",
                         help="Show this help message and exit")
    options.add_argument("-s", "--serverUrl", metavar="url", nargs="?",
                         help="Dialog server URL", default='dlg.api.nuance.com:443')
    options.add_argument('--modelUrn', nargs="?", default='urn:nuance-mix:tag:model/CallCenter/mix.dialog',
                         help="Dialog App URN, e.g. urn:nuance-mix:tag:model/CallCenter/mix.dialog")
    options.add_argument("--inputMode", nargs="?",
                         help="Input mode, 'text' or 'voice'", default='text')
    options.add_argument("--outputMode", nargs="?",
                         help="Input mode, 'text' or 'voice'", default='text')

    return parser.parse_args()

def execute_stream_request(stub, session_id, selector_dict={}, payload_dict={}):
    execute_responses = stub.ExecuteStream(build_stream_input(session_id,
                                                              selector_dict,
                                                              payload_dict))
    log.debug(f'execute_responses: {execute_responses}')
    responses = []
    audio = bytearray(b'')

    for execute_response in execute_responses:
        if execute_response:
            response = MessageToDict(execute_response.response)
            if response: responses.append(response)
        audio += execute_response.audio.audio
        audiolen = len(audio)
    log.debug(f'ExecuteStream responses: {responses}')
    log.debug(f'ExecuteStream audio len: {audiolen}')
    return responses, audio

def build_stream_input(session_id, selector_dict={}, payload_dict={}):
    selector = Selector(channel=selector_dict.get('channel'), 
                        library=selector_dict.get('library'),
                        language=selector_dict.get('language'))

    audio_input = payload_dict.get('user_input').get('userAudio')
    text_input = payload_dict.get('user_input').get('userText')
    data_input = payload_dict.get('user_input').get('requested_data')
    
    try:
        with open(audio_input, mode='rb') as file:
            audio_buffer = file.read()
        # Hard code packet_size_byte for simplicity sake (approximately 200ms of 8KHz mono audio)
        packet_size_byte = 3217
        audio_size = sys.getsizeof(audio_buffer)
        audio_packets = [ audio_buffer[x:x + packet_size_byte] for x in range(0, audio_size, packet_size_byte) ]

        # For simplicity sake, let's assume the audio file is PCM 8KHz
        user_input = None
        asr_control_v1 = {'audio_format': {'pcm': {'sample_rate_hz': 16000}}}

    except:
        # Text interpretation as normal
        log.debug(f'No audio provided:{audio_input} defaulting to text: {text_input}')
        audio_packets = [b'']
        user_input = UserInput(user_text=text_input)
        asr_control_v1 = None
        
    # Build execute request object
    if( data_input ):
        user_input = UserInput(user_text="")        
        log.debug(f'RequestedData: {data_input}')
        data_struct = Struct()

        # RequestedData: {'id': 'DataAccess', 'data': {'KEY': 'VALUE', 'returnCode': '0'}}
        for k in data_input.get('data').keys():
            v = data_input.get('data').get(k)
            data_struct.update({k:v})            
                
        requested_data = RequestData(id=data_input.get('id'), data=data_struct)
        execute_payload = ExecuteRequestPayload(user_input=user_input, requested_data=requested_data)
    else:
        execute_payload = ExecuteRequestPayload(user_input=user_input)

    execute_request = ExecuteRequest(session_id=session_id, 
                                     selector=selector, 
                                     payload=execute_payload)

    # For simplicity sake, let's assume the audio file is PCM 16KHz
    tts_control_v1 = {'voice': {'name':'Paulina-Ml', 'model':'enhanced'},
                      'audio_params': {'audio_format': {'pcm': {'sample_rate_hz': 16000}}}}
    first_packet = True
    for audio_packet in audio_packets:
        if first_packet:
            first_packet = False

            # Only first packet should include the request header
            stream_input = StreamInput(
                request=execute_request,
                asr_control_v1=asr_control_v1,
                tts_control_v1=tts_control_v1,
                audio=audio_packet
                )
        else:
            stream_input = StreamInput(audio=audio_packet)

        yield stream_input

def read_session_id_from_response(response_obj):
    try:
        session_id = response_obj.get('payload').get('sessionId', None)
    except Exception as e:
        raise Exception("Invalid JSON Object or response object")
    if session_id:
        return session_id
    else:
        raise Exception("Session ID is not present or some error occurred")
  
def stop_request(stub, session_id=None):
    stop_req = StopRequest(session_id=session_id)
    log.debug(f'Stop Request: {stop_req}')
    stop_response, call = stub.Stop.with_call(stop_req)
    response = MessageToDict(stop_response)
    log.debug(f'Stop Response: {response}')
    return response, call

def main():
    args = parse_args()
    log_level = logging.DEBUG
    logging.basicConfig(
        format='%(asctime)s %(levelname)-5s: %(message)s', level=log_level)

    now = datetime.datetime.now(timezone('EST'))
    log_dir = "audio/"
    log_pref = now.strftime("audio/MixApp-%H-%M")

    os.makedirs(log_dir, exist_ok=True)
    log.debug("LogDir:{}".format(log_dir))
    
    with create_channel(args) as channel:
        stub = DialogServiceStub(channel)
        model_ref_dict = {
            "uri": args.modelUrn,
            "type": 0
        }
        selector_dict = {
            "channel": "default",
            "language": "es-US",
            "library": "default"
        }
        response, call = start_request(stub, 
                            model_ref_dict=model_ref_dict, 
                            session_id=None,
                            selector_dict=selector_dict
                        )

        session_id = read_session_id_from_response(response)
        log.debug(f'Session: {session_id}')        
        assert call.code() == StatusCode.OK

        log.debug(f'Initial request, no input from the user to get initial prompt')
        payload_dict = {
            "user_input": {
                "userText": None,
                "userAudio": None,
                "userData": None                
            }
        }
        responses, audio = execute_stream_request(stub,
                                                 session_id=session_id, 
                                                 selector_dict=selector_dict,
                                                 payload_dict=payload_dict
        )
        assert call.code() == StatusCode.OK

        tts_audio_index=0
        asr_audio_index=0
        call_ended = False

        # Audio format for TTS generated files
        sampleRate=16000
        bitsPerSample=16
        channels=1
        audioformat=1

        while not call_ended:
            # Writes audio if a TTS response was generated by previous interaction
            audiolen=len(audio)
            if audiolen and args.outputMode=='voice':
                tts_audio_index=tts_audio_index+1
                file_name = "{}-{}-tts_utt{}".format(log_pref,session_id, str(tts_audio_index).zfill(4))
                audio_file = open("{}.wav".format(file_name), "wb")            
                waveheader = genHeader(sampleRate,bitsPerSample,channels,audiolen,audioformat)
                audio_file.write(waveheader)
                audio_file.write(audio)
                audio_file.close()
                #time.sleep(0.2)
                log.debug(f'TTS saved: {file_name}, audio length: {audiolen}')
                
                wave_obj = sa.WaveObject.from_wave_file(file_name + '.wav')
                play_obj = wave_obj.play()
                play_obj.wait_done()  # Wait until sound has finished playing                                       
                
            if responses[0]:
                if 'endAction' in responses[0].get('payload').keys():
                    log.debug(f'End action request')
                    call_ended = True
                    break
            
                if 'daAction' in responses[0].get('payload').keys():
                    log.debug(f'Start of Data action request')

                    # Sample DB request from Mix Dialog
                    # https://pypi.org/project/sportinf/
                    try:
                        # 'payload': {'daAction': {'id': 'DataAccess', 'message': {}, 'view': {}, 'data': {'AthleteName': 'Lionel Messi', 'LastIntent': 'Nationality'}
                        intent = responses[0].get('payload').get('daAction').get('data').get('LastIntent')
                        athlete_name = responses[0].get('payload').get('daAction').get('data').get('AthleteName')

                        log.debug(f"DataAccess requested: {intent} for athlete: {athlete_name}")

                        if(intent == 'AthleteNameOnly'):
                            intent = 'Sport'

                        info = SportInfo(option="Information about player", player_name=athlete_name).sport_info()[intent]

                        if(intent == 'BirthLocation'):
                            athlete_info =  '{} nació en {}.'.format(athlete_name, info)
                        if(intent == 'Nationality'):
                            athlete_info =  '{} tiene nacionalidad de {}.'.format(athlete_name, info)
                        if(intent == 'Team'):
                            athlete_info =  '{} juega para {}.'.format(athlete_name, info)
                        if(intent == 'Sport'):
                            athlete_info =  '{} es deportista de {}.'.format(athlete_name, info)
                        if(intent == 'dateBorn'):
                            # Adjust date to the format expected by TTS SSLM tag: <say-as> 
                            dob = datetime.datetime.strptime(info,'%Y-%m-%d').strftime('%m/%d/%Y')
                            if(args.outputMode=='voice'):
                                athlete_info =  '{} nació el <say-as interpret-as="date">{}</say-as>.'.format(athlete_name, dob)
                            else:
                                athlete_info =  '{} nació el {}'.format(athlete_name, dob)
                        if(intent == 'Position'):
                            athlete_info =  '{} juega la posición de {}.'.format(athlete_name, info)
                    except:
                        athlete_info = 'No encontré información al respecto'

                    payload_dict = {
                        "user_input": {
                            "userText": None,
                            "userAudio": None,
                            "requested_data": {
                                "id": "DataAccess",
                                "data": { 
                                          "AthleteInfo": athlete_info,
                                          "returnCode": "0"                                          
                                      }
                            }
                        }
                    }

                    responses, audio = execute_stream_request(stub, session_id, selector_dict, payload_dict)
                    log.debug(f'End of Data action request')
                    continue

                if 'qaAction' in responses[0].get('payload').keys():
                    # 'payload': {'qaAction': {'message': {'nlg': [{'text': '¿Que información sobre algún deportista te interesa saber?'}]...
                    qa_prompt = "\n" + responses[0].get('payload').get('qaAction').get('message').get('visual')[0].get('text')
                    if 'messages' in responses[0].get('payload').keys():
                        qa_prompt = responses[0].get('payload').get('messages')[0].get('nlg')[0].get('text') + "\n" + qa_prompt

                    click.secho(qa_prompt, fg='yellow')                        

                    if(args.inputMode == 'voice'):
                        asr_audio_index = asr_audio_index + 1
                        user_audio = "{}-{}-asr_utt{}.wav".format(log_pref,session_id, str(asr_audio_index).zfill(4))
                        record_audio(user_audio)

                        log.debug(f'QA action request, passing in user input {user_audio}')
                        payload_dict = {
                            "user_input": {
                                "userText": "terminar",
                                "userAudio": user_audio,
                                "userData": None
                            }
                        }
                    else:
                        user_text = input(">")
                        log.debug(f'QA action request, passing in user input {user_text}')
                        payload_dict = {
                            "user_input": {
                                "userText": user_text
                            }
                        }                    
            
                    responses, audio = execute_stream_request(stub, session_id, selector_dict, payload_dict)
                    log.debug(f'End of QA action request')

        if not call_ended:
            response, call = stop_request(stub,
                                          session_id=session_id
            )
            assert call.code() == StatusCode.OK
            
if __name__ == '__main__':
    main()
