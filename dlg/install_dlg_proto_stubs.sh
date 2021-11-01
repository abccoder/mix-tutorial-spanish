unzip -o ../proto_files/nuance_dialog_dialogservice_protos_v1.zip

echo "Pulling support files"
mkdir -p google/api
curl https://raw.githubusercontent.com/googleapis/googleapis/master/google/api/annotations.proto > google/api/annotations.proto
curl https://raw.githubusercontent.com/googleapis/googleapis/master/google/api/http.proto > google/api/http.proto
echo "generate the stubs for support files"
python -m grpc_tools.protoc --proto_path=./ --python_out=./ google/api/http.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=./ google/api/annotations.proto
echo "generate the stubs for the DLGaaS gRPC files"
python -m grpc_tools.protoc --proto_path=./ --python_out=. --grpc_python_out=. nuance/dlg/v1/dlg_interface.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=. --grpc_python_out=. nuance/dlg/v1/dlg_messages.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=. --grpc_python_out=. nuance/dlg/v1/common/dlg_common_messages.proto
echo "generate the stubs for the ASRaaS gRPC files"
python -m grpc_tools.protoc --proto_path=./ --python_out=. --grpc_python_out=. nuance/asr/v1/recognizer.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=. --grpc_python_out=. nuance/asr/v1/resource.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=. --grpc_python_out=. nuance/asr/v1/result.proto
echo "generate the stubs for the TTSaaS gRPC files"
python -m grpc_tools.protoc --proto_path=./ --python_out=. --grpc_python_out=. nuance/tts/v1/nuance_tts_v1.proto
echo "generate the stubs for the NLUaaS gRPC files"
python -m grpc_tools.protoc --proto_path=./ --python_out=. --grpc_python_out=. nuance/nlu/v1/runtime.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=. --grpc_python_out=. nuance/nlu/v1/result.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=. --grpc_python_out=. nuance/nlu/v1/interpretation-common.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=. --grpc_python_out=. nuance/nlu/v1/single-intent-interpretation.proto
python -m grpc_tools.protoc --proto_path=./ --python_out=. --grpc_python_out=. nuance/nlu/v1/multi-intent-interpretation.proto
