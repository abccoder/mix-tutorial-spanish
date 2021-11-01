# Usage: bash run-tts-client.sh "gracias por llamar a nuestra aplicación de demostración, cómo puedo ayudarte?"

CLIENT_ID=<client_id>
SECRET=<secret>

export MY_TOKEN="`curl -s -u $CLIENT_ID:$SECRET \
https://auth.crt.nuance.com/oauth2/token \
-d 'grant_type=client_credentials' -d 'scope=tts' \
| python -c 'import sys, json; print(json.load(sys.stdin)["access_token"])' | dos2unix  `"

echo $MY_TOKEN

python ./my-tts-client.py --server_url tts.api.nuance.com:443 \
  --token $MY_TOKEN \
  --name 'Paulina-Ml' \
  --model 'enhanced' \
  --text "$1" \
  --output_wav_file 'salida.wav'