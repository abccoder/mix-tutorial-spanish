# mix-tutorial-spanish

Create a free account for Nuance Mix. Please note that a business email address is required.

https://account.crt.nuance.com/auth/realms/mix/protocol/openid-connect/registrations?client_id=portal-connect-auth&response_type=code&redirect_uri=https://mix.nuance.com/v3/

| Resource	| Link |
| --- | --- |
| Forums	| https://community.mix.nuance.com |
| Documentation |	https://docs.mix.nuance.com |
| GitHub	 | https://github.com/nuance-communications |
| Status	 | https://status.mix.nuance.com |

## Sample client applications for Nuance Mix Services
 
### Mix Projects for Applications 
Before developing your gRPC application, you need a Mix project that provides a dialog application as well as authorization credentials.

https://docs.mix.nuance.com/mix-starting/#quick-start

https://docs.mix.nuance.com/mix-dialog/#creating-mix-dialog-applications

This sections takes you through the process of creating a simple coffee application.

- **projects/order_coffee**:  Project files for the OrderCoffe Demo
- **projects/athletes_info**: Project files for the AthletesInfo Demo

### Application Code

- **asr**: Automatic Speech Recognition as a Service (ASRaas)
- **nlu**: Natural Language Understanding as a Service (NLUaas)
- **dlg**: Dialog as a Service (DLGaaS)
- **tts**: Text to Speech as a Service (TTSaaS)

You can try out this simple client applications. 
To run them, you need:
- Python 3.6 or later.
- Your client ID and secret from Prerequisites from Mix
- The generated Python stub files from gRPC setup, as described at:
  - **asr**: https://docs.mix.nuance.com/asr-grpc/v1/#prerequisites-from-mix
  - **nlu**: https://docs.mix.nuance.com/nlu-grpc/v1/#prerequisites-from-mix
  - **dlg**: https://docs.mix.nuance.com/dialog-grpc/v1/#prerequisites-from-mix
  - **tts**: https://docs.mix.nuance.com/tts-grpc/v1/#prerequisites-from-mix

Install required Python modules

```
pip install sportinf

pip install pyaudio

pip install simpleaudio
```

Check shell scripts for info on how to install dependencies & execute the python apps.

```
asr/install_asr_proto_stubs.sh
asr/run-asr-client.sh

dlg/install_dlg_proto_stubs.sh
dlg/run-athlete-info-client.sh
dlg/run-mix-client.sh

nlu/install_nlu_proto_stubs.sh
nlu/run-nlu-client.sh

tts/install_tts_proto_stubs.sh
tts/run-tts-client.sh
```
run-*-client.sh: shell script should be located and executed right from the directory above your proto files and stubs.

