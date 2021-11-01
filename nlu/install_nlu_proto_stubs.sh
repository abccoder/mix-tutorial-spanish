# Check https://docs.mix.nuance.com/nlu-grpc/v1/#grpc-setup for details
unzip -o ../proto_files/nuance_nlu_runtime_protos_v1.zip
unzip -o ../proto_files/nuance_nlu_wordset_protos_v1.zip

mkdir -p google/api
curl https://raw.githubusercontent.com/googleapis/googleapis/master/google/api/annotations.proto > google/api/annotations.proto
curl https://raw.githubusercontent.com/googleapis/googleapis/master/google/api/http.proto > google/api/http.proto

echo "Generate the stubs for support files"
python -m grpc_tools.protoc --proto_path=./ --python_out=./ google/api/http.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=./ google/api/annotations.proto

echo "Generate client stubs from proto files"
python -m grpc_tools.protoc --proto_path=./ --python_out=./ --grpc_python_out=./ nuance/nlu/v1/runtime.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=./  nuance/nlu/v1/result.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=./  nuance/nlu/v1/interpretation-common.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=./  nuance/nlu/v1/single-intent-interpretation.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=./  nuance/nlu/v1/multi-intent-interpretation.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=./  --grpc_python_out=./ nuance/nlu/wordset/v1beta1/wordset.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=./  nuance/nlu/common/v1beta1/job.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=./  nuance/nlu/common/v1beta1/resource.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=./  nuance/rpc/status.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=./  nuance/rpc/status_code.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=./  nuance/rpc/error_details.proto
