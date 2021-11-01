#!/usr/bin/env python3

# Import functions
import sys
import grpc
import argparse
import simpleaudio as sa
from nuance.tts.v1.synthesizer_pb2 import *
from nuance.tts.v1.synthesizer_pb2_grpc import *
from google.protobuf import text_format

# Generates a .wav file header
def generate_wav_header(sample_rate, bits_per_sample, channels, audio_len, audio_format):
    # (4byte) Marks file as RIFF
    o = bytes("RIFF", 'ascii')
    # (4byte) File size in bytes excluding this and RIFF marker
    o += (audio_len + 36).to_bytes(4, 'little')
    # (4byte) File type
    o += bytes("WAVE", 'ascii')
    # (4byte) Format Chunk Marker
    o += bytes("fmt ", 'ascii')
    # (4byte) Length of above format data
    o += (16).to_bytes(4, 'little')
    # (2byte) Format type (1 - PCM)
    o += (audio_format).to_bytes(2, 'little')
    # (2byte) Will always be 1 for TTS
    o += (channels).to_bytes(2, 'little')
    # (4byte)
    o += (sample_rate).to_bytes(4, 'little')
    o += (sample_rate * channels * bits_per_sample // 8).to_bytes(4, 'little')  # (4byte)
    o += (channels * bits_per_sample // 8).to_bytes(2,'little')               # (2byte)
    # (2byte)
    o += (bits_per_sample).to_bytes(2, 'little')
    # (4byte) Data Chunk Marker
    o += bytes("data", 'ascii')
    # (4byte) Data size in bytes
    o += (audio_len).to_bytes(4, 'little')

    return o

# Define synthesis request
def create_synthesis_request(name, model, text, ssml, sample_rate, send_log_events, client_data):
    request = SynthesisRequest()

    request.voice.name = name
    request.voice.model = model

    pcm = PCM(sample_rate_hz=sample_rate)
    request.audio_params.audio_format.pcm.CopyFrom(pcm)

    if text:
        request.input.text.text = text
    elif ssml:
        request.input.ssml.text = ssml
    else:
        raise RuntimeError("No input text or SSML defined.")

    request.event_params.send_log_events = send_log_events

    return request


def main():
    parser = argparse.ArgumentParser(
        prog="simple-mix-client.py",
        usage="%(prog)s [-options]",
        add_help=False,
        formatter_class=lambda prog: argparse.HelpFormatter(
            prog, max_help_position=45, width=100)
    )

    # Set arguments
    options = parser.add_argument_group("options")
    options.add_argument("-h", "--help", action="help",
                         help="Show this help message and exit")
    options.add_argument("--server_url", nargs="?",
                         help="Server hostname (default=localhost)", default="localhost:8080")
    options.add_argument("--token", nargs="?",
                         help="Access token", required=True)
    options.add_argument("--name", nargs="?", help="Voice name", required=True)
    options.add_argument("--model", nargs="?",
                         help="Voice model", required=True)
    options.add_argument("--sample_rate", nargs="?",
                         help="Audio sample rate (default=22050)", type=int, default=22050)
    options.add_argument("--text", nargs="?", help="Input text")
    options.add_argument("--ssml", nargs="?", help="Input SSML")
    options.add_argument("--send_log_events",
                         action="store_true", help="Subscribe to Log Events")
    options.add_argument("--output_wav_file", nargs="?",
                         help="Destination file path for synthesized audio")
    options.add_argument("--client_data", nargs="?",
                         help="Client information in key value pairs")

    args = parser.parse_args()

    # Create channel and stub 
    call_credentials = grpc.access_token_call_credentials(args.token)
    channel_credentials = grpc.composite_channel_credentials(
        grpc.ssl_channel_credentials(), call_credentials)

    # Send request and process results
    with grpc.secure_channel(args.server_url, credentials=channel_credentials) as channel:
        stub = SynthesizerStub(channel)
        request = create_synthesis_request(name=args.name, model=args.model, text=args.text,
            ssml=args.ssml, sample_rate=args.sample_rate, send_log_events=args.send_log_events,
            client_data=args.client_data)
        stream_in = stub.Synthesize(request)
        audio_file = None
        wav_header = None
        total_audio_len = 0
        try:
            if args.output_wav_file:
                audio_file = open(args.output_wav_file, "wb")
                # Write an empty wav header for now, until we know the final audio length
                wav_header = generate_wav_header(sample_rate=args.sample_rate, bits_per_sample=16, channels=1, audio_len=0, audio_format=1)
                audio_file.write(wav_header)
            for response in stream_in:
                if response.HasField("audio"):
                    print("Received audio: %d bytes" % len(response.audio))
                    total_audio_len = total_audio_len + len(response.audio)
                    if(audio_file):
                        audio_file.write(response.audio)
                elif response.HasField("events"):
                    print("Received events")
                    print(text_format.MessageToString(response.events))
                else:
                    if response.status.code == 200:
                        print("Received status response: SUCCESS")
                    else:
                        print("Received status response: FAILED")
                        print("Code: {}, Message: {}".format(response.status.code, response.status.message))
                        print('Error: {}'.format(response.status.details))
        except Exception as e:
            print(e)
        if audio_file:
            wav_header = generate_wav_header(sample_rate=args.sample_rate, bits_per_sample=16, channels=1, audio_len=total_audio_len, audio_format=1)
            audio_file.seek(0, 0)
            audio_file.write(wav_header)
            audio_file.close()
            print("Saved audio to {}".format(args.output_wav_file))

            wave_obj = sa.WaveObject.from_wave_file(args.output_wav_file)
            play_obj = wave_obj.play()
            play_obj.wait_done()  # Wait until sound has finished playing                                       

if __name__ == '__main__':
    main()