#!/bin/bash

# Usage: bash run-asr-client.sh <context-tag> <audio-file>
# Example1: bash run-asr-client.sh CoffeeOrderDemo test1.wav
# Example2: bash run-asr-client.sh AthleteInfoDemo test2.wav

CLIENT_ID=<client_id>
SECRET=<secret>

export MY_TOKEN="`curl -s -u $CLIENT_ID:$SECRET \
https://auth.crt.nuance.com/oauth2/token \
-d 'grant_type=client_credentials' -d 'scope=asr nlu tts dlg' \
| python -c 'import sys, json; print(json.load(sys.stdin)["access_token"])' | dos2unix  `"

echo $MY_TOKEN

python ./my-asr-client.py $1 $MY_TOKEN $2
