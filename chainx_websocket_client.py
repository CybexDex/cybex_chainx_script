from websocket import create_connection
import json
import logging

class RPCError(Exception):
    pass

class WebsocketClient():
    def __init__(self, websocket_url):
        self.ws = create_connection(websocket_url)
        self.request_id = 0
   
    def request(self, method_name, params):
        payload = {
            'id': self.request_id,
            "jsonrpc":"2.0",
            'method': method_name,
            'params': params
        }
        request_string = json.dumps(payload) 
        logging.info('> {}'.format(request_string))
        #print('> {}'.format(request_string))
	try:
            self.ws.send(request_string)
            self.request_id += 1
	except:
	    raise RPCError(request_string)
	try:
            reply =  self.ws.recv()
	except:
	    raise RPCError("ws.recv error when send req: " + request_string)
        #print('< {}'.format(reply))

        ret = {}
        try:
            ret = json.loads(reply, strict=False)
        except ValueError:
            raise ValueError("Client returned invalid format. Expected JSON!")

        
        if 'error' in ret:
            if 'detail' in ret['error']:
                raise RPCError(ret['error']['detail'])
            else:
                raise RPCError(ret['error']['message'])
        else:
            return ret["result"]
    def close(self):
        self.ws.close()



import config

client = WebsocketClient(config.WEBSOCKET_URL)
