# mix-tutorial-spanish
# Sample client applications for Nuance Mix Services

asr: Automatic Speech Recognition as a Service (ASRaas)
nlu: Natural Language Understanding as a Service (NLUaas)
dlg: Dialog as a Service (DLGaaS)
tts: Text to Speech as a Service (TTSaaS)

Check official Mix Documentation at: https://docs.mix.nuance.com/runtime-services/#runtime-apis-quick-reference

You can try out this simple client applications. 
To run them, you need:

Python 3.6 or later.

The generated Python stub files from gRPC setup.
Your client ID and secret from Prerequisites from Mix.

Check shell scripts for info on how to install dependencies & execute the python apps.

asr/install_asr_proto_stubs.sh
asr/run-asr-client.sh

dlg/install_dlg_proto_stubs.sh
dlg/run-athlete-info-client.sh
dlg/run-mix-client.sh

nlu/install_nlu_proto_stubs.sh
nlu/run-nlu-client.sh

tts/install_tts_proto_stubs.sh
tts/run-tts-client.sh

run-*-client.sh: shell script at the right into the directory above your proto files and stubs.

