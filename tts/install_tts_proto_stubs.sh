# Check https://docs.mix.nuance.com/tts-grpc/v1/#grpc-setup for details
unzip -o ../proto_files/nuance_tts_and_storage_protos.zip

echo Generate Python stubs from TTS proto files
python -m grpc_tools.protoc --proto_path=./ --python_out=./ --grpc_python_out=./ nuance/tts/v1/synthesizer.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=./ --grpc_python_out=./ nuance/tts/storage/v1beta1/storage.proto

echo Generate Python stubs from RPC proto files
python -m grpc_tools.protoc --proto_path=./ --python_out=./ nuance/rpc/error_details.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=./ nuance/rpc/status_code.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=./ nuance/rpc/status.proto
