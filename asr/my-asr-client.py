#!/usr/bin/env python3
import pyaudio
import click
import sys, wave, grpc, traceback
from time import sleep
from nuance.asr.v1.resource_pb2 import *
from nuance.asr.v1.result_pb2 import *
from nuance.asr.v1.recognizer_pb2 import *
from nuance.asr.v1.recognizer_pb2_grpc import *

# Collect arguments from user
hostaddr = "asr.api.nuance.com:443"
context_tag = access_token = audio_file = None
try:
    context_tag = sys.argv[1]
    access_token = sys.argv[2]
    audio_file = sys.argv[3]
except Exception as e:
    print(f'usage: {sys.argv[0]} <hostaddr> <token> <audio_file.wav>')
    exit(1)

# Declare a DLM that exists in a Mix project
custom_dlm = RecognitionResource(
    external_reference = ResourceReference(
        type = 'DOMAIN_LM',
        uri = 'urn:nuance-mix:tag:model/{}/mix.asr?=language=spa-XLA'.format(context_tag)),
    weight_value = 0.7)


# Send recognition request parameters and audio
def client_stream(wf):
    try:
        # Set recognition parameters
        init = RecognitionInitMessage(
            parameters = RecognitionParameters(
                language = 'es-US', 
                topic = 'GEN',
                audio_format = AudioFormat(pcm=PCM(sample_rate_hz=wf.getframerate())),
                result_type = 'FINAL', 
                utterance_detection_mode = 'MULTIPLE',
                recognition_flags = RecognitionFlags(
                    auto_punctuate = True)),
            resources = [custom_dlm],
        )
        yield RecognitionRequest(recognition_init_message=init)

        # Simulate a realtime audio stream using an audio file
        print(f'stream {wf.name}')
        packet_duration = 0.020
        packet_samples = int(wf.getframerate() * packet_duration)
        for packet in iter(lambda: wf.readframes(packet_samples), b''):
            yield RecognitionRequest(audio=packet)
            sleep(packet_duration)
        print('stream complete')
    except CancelledError as e:
        print(f'client stream: RPC canceled')
    except Exception as e:
        print(f'client stream: {type(e)}')
        traceback.print_exc()

# On windows, records an audio file using pyaudio for demo purposes
# http://people.csail.mit.edu/hubert/pyaudio/#record-example

chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
fs = 16000  # Record at 16000 samples per second
seconds = 6
filename = audio_file

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

click.secho('Finished recording..', fg='red')

# Save the recorded data as a WAV file
wf = wave.open(filename, 'wb')
wf.setnchannels(channels)
wf.setsampwidth(p.get_sample_size(sample_format))
wf.setframerate(fs)
wf.writeframes(b''.join(frames))
wf.close()

# Check audio file attributes and open secure channel with token
wf=wave.open(audio_file, 'r')
assert wf.getsampwidth() == 2, f'{audio_file} is not linear PCM'
assert wf.getframerate() in [8000, 16000], f'{audio_file} sample rate must be 8000 or 16000'
assert wf.getnchannels() == 1, f'{audio_file} is not a mono audio file'
setattr(wf, 'name', audio_file)
call_credentials = grpc.access_token_call_credentials(access_token)
ssl_credentials = grpc.ssl_channel_credentials()
channel_credentials = grpc.composite_channel_credentials(ssl_credentials, call_credentials)     
with grpc.secure_channel(hostaddr, credentials=channel_credentials) as channel:
    stub = RecognizerStub(channel)
    stream_in = stub.Recognize(client_stream(wf))
    try:
        # Iterate through messages returned from server
        for message in stream_in:
            if message.HasField('status'):
                if message.status.details:
                        print(f'{message.status.code} {message.status.message} - {message.status.details}')
                else:
                        print(f'{message.status.code} {message.status.message}')
            elif message.HasField('result'):
                restype = 'partial' if message.result.result_type else 'final'
                print(f'{restype}: {message.result.hypotheses[0].formatted_text}')
    except StreamClosedError:
        pass
    except Exception as e:
        print(f'server stream: {type(e)}')
        traceback.print_exc()
