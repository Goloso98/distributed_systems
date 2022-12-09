# install

https://grpc.io/docs/languages/python/quickstart/

`$ python -m grpc_tools.protoc -I../../protos --python_out=. --pyi_out=. --grpc_python_out=. ../../protos/helloworld.proto`

`python -m grpc_tools.protoc --proto_path=proto/ --python_out=main/ --pyi_out=main/ --grpc_python_out=main/ proto/*.proto`

