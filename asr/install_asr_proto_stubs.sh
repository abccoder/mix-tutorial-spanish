unzip -o ../proto_files/nuance_asr_rpc_protos.zip

python -m grpc_tools.protoc --proto_path=./ --python_out=./ --grpc_python_out=./ nuance/asr/v1/recognizer.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=./ nuance/asr/v1/resource.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=./ nuance/asr/v1/result.proto

echo Generate RPC client stubs
python -m grpc_tools.protoc --proto_path=./ --python_out=./ nuance/rpc/status.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=./ nuance/rpc/status_code.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=./ nuance/rpc/error_details.proto