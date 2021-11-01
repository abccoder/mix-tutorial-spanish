import argparse
import logging

import uuid

from google.protobuf.json_format import MessageToJson, MessageToDict

from grpc import StatusCode

from nuance.dlg.v1.common.dlg_common_messages_pb2 import *
from nuance.dlg.v1.dlg_messages_pb2 import *
from nuance.dlg.v1.dlg_interface_pb2 import *
from nuance.dlg.v1.dlg_interface_pb2_grpc import *

log = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(
        prog="dlg_client.py",
        usage="%(prog)s [-options]",
        add_help=False,
        formatter_class=lambda prog: argparse.HelpFormatter(
            prog, max_help_position=45, width=100)
    )

    options = parser.add_argument_group("options")
    options.add_argument("-h", "--help", action="help",
                         help="Show this help message and exit")
    options.add_argument("--token", nargs="?", help=argparse.SUPPRESS)
    options.add_argument("-s", "--serverUrl", metavar="url", nargs="?",
                         help="Dialog server URL, default=localhost:8080", default='localhost:8080')
    options.add_argument('--modelUrn', nargs="?",
                         help="Dialog App URN, e.g. urn:nuance:mix/eng-USA/A2_C16/mix.dialog")
    options.add_argument("--textInput", metavar="file", nargs="?",
                         help="Text to preform interpretation on")

    return parser.parse_args()

def create_channel(args):    
    log.debug("Adding CallCredentials with token %s" % args.token)
    call_credentials = grpc.access_token_call_credentials(args.token)

    log.debug("Creating secure gRPC channel")
    channel_credentials = grpc.ssl_channel_credentials()
    channel_credentials = grpc.composite_channel_credentials(channel_credentials, call_credentials)
    channel = grpc.secure_channel(args.serverUrl, credentials=channel_credentials)

    return channel

def read_session_id_from_response(response_obj):
    try:
        session_id = response_obj.get('payload').get('sessionId', None)
    except Exception as e:
        raise Exception("Invalid JSON Object or response object")
    if session_id:
        return session_id
    else:
        raise Exception("Session ID is not present or some error occurred")


def start_request(stub, model_ref_dict, session_id, selector_dict={}):
    selector = Selector(channel=selector_dict.get('channel'), 
                        library=selector_dict.get('library'),
                        language=selector_dict.get('language'))
    start_payload = StartRequestPayload(model_ref=model_ref_dict)
    start_req = StartRequest(session_id=session_id, 
                        selector=selector, 
                        payload=start_payload)
    log.debug(f'Start Request: {start_req}')
    start_response, call = stub.Start.with_call(start_req)
    response = MessageToDict(start_response)
    log.debug(f'Start Request Response: {response}')
    return response, call

def execute_request(stub, session_id, selector_dict={}, payload_dict={}):
    selector = Selector(channel=selector_dict.get('channel'), 
                        library=selector_dict.get('library'),
                        language=selector_dict.get('language'))
    input = UserInput(user_text=payload_dict.get('user_input').get('userText'))
    execute_payload = ExecuteRequestPayload(
                        user_input=input)
    execute_request = ExecuteRequest(session_id=session_id, 
                        selector=selector, 
                        payload=execute_payload)
    log.debug(f'Execute Request: {execute_payload}')
    execute_response, call = stub.Execute.with_call(execute_request)
    response = MessageToDict(execute_response)
    log.debug(f'Execute Response: {response}')
    return response, call

def stop_request(stub, session_id=None):
    stop_req = StopRequest(session_id=session_id)
    log.debug(f'Stop Request: {stop_req}')
    stop_response, call = stub.Stop.with_call(stop_req)
    response = MessageToDict(stop_response)
    log.debug(f'Stop Response: {response}')
    return response, call

def main():
    args = parse_args()
    log_level = logging.DEBUG
    logging.basicConfig(
        format='%(asctime)s %(levelname)-5s: %(message)s', level=log_level)
    with create_channel(args) as channel:
        stub = DialogServiceStub(channel)
        model_ref_dict = {
            "uri": args.modelUrn,
            "type": 0
        }
        selector_dict = {
            "channel": "default",
            "language": "es-US",
            "library": "default"
        }
        response, call = start_request(stub, 
                            model_ref_dict=model_ref_dict, 
                            session_id=None,
                            selector_dict=selector_dict
                        )
        session_id = read_session_id_from_response(response)
        log.debug(f'Session: {session_id}')
        assert call.code() == StatusCode.OK
        log.debug(f'Initial request, no input from the user to get initial prompt')
        payload_dict = {
            "user_input": {
                "userText": None
            }
        }
        response, call = execute_request(stub, 
                            session_id=session_id, 
                            selector_dict=selector_dict,
                            payload_dict=payload_dict
                        )
        assert call.code() == StatusCode.OK
        log.debug(f'Second request, passing in user input')
        payload_dict = {
            "user_input": {
                "userText": args.textInput
            }
        }
        response, call = execute_request(stub, 
                            session_id=session_id, 
                            selector_dict=selector_dict,
                            payload_dict=payload_dict
                        )
        assert call.code() == StatusCode.OK

if __name__ == '__main__':
    main()
