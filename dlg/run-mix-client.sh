#!/bin/bash

# Invokes dlg_client.py using sample app (Coffee Demo) in text mode for a single intereaction.
#
# Usage: bash run-mix-client.sh "urn:nuance-mix:tag:model/CoffeeOrderDemo/mix.dialog" "dame un capuchino grande por favor"

# Remember to change the colon (:) in your CLIENT_ID to code %3A
CLIENT_ID=<client_id>
SECRET=<secret>
export MY_TOKEN="`curl -s -u "$CLIENT_ID:$SECRET" "https://auth.crt.nuance.com/oauth2/token" \
-d 'grant_type=client_credentials' -d 'scope=dlg' \
| python -c 'import sys, json; print(json.load(sys.stdin)["access_token"])'|dos2unix`"

python dlg_client.py --serverUrl "dlg.api.nuance.com:443" --token $MY_TOKEN --modelUrn "$1" --textInput "$2"
