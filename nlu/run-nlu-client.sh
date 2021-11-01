#!/bin/bash

# Usage: bash run-nlu-client.sh <context-tag> <text>
# Example1: bash run-nlu-client.sh CoffeeOrderDemo "quiero un capuchino grande"
# Example2: bash run-nlu-client.sh AthleteInfoDemo "donde nació saul alvarez?"

CLIENT_ID=<client_id>
SECRET=<secret>
export TOKEN="`curl -s -u "$CLIENT_ID:$SECRET" "https://auth.crt.nuance.com/oauth2/token" \
-d 'grant_type=client_credentials' -d 'scope=tts nlu asr' \
| python -c 'import sys, json; print(json.load(sys.stdin)["access_token"])'|dos2unix`"

python nlu_client.py --serverUrl nlu.api.nuance.com:443 --token $TOKEN \
--modelUrn "urn:nuance-mix:tag:model/$1/mix.nlu?=language=spa-XLA" \
--textInput "$2"