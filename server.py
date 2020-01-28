from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from urllib.parse import parse_qs
from urllib.parse import unquote
import json
from narouresearch.networks.styleEncoder.model import StyleDisperser
from narouresearch.conversion.convert import char2ID as char2id, ID2char as id2char
import torch

PORT = 7604

BOS, EOS, UNK = 0,1,2
if torch.cuda.is_available():
    device = torch.device("cuda")
else: device = torch.device("cpu")
def transform(batchData):
    return torch.tensor([[char2id(c) for c in data]+[EOS] for data in batchData]).to(device)
class stylemodel:
    def __init__(self):
        print('model loading...')
        self.model = StyleDisperser(weights=None, method="GRU", input_size=24498, hidden_size=128, output_size=3, device=device, margin=0.75)
        self.model.load_state_dict(torch.load("interface/7_0.6073_0.9461.weight", map_location=torch.device('cpu')))
        self.model.to(device)
        self.model.eval()
    def __call__(self, text):
        with torch.no_grad():
            return self.model.inference(transform(text)).cpu()

model = stylemodel()

class MyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.make_data()
    def do_GET(self):
        if self.path == '/':
            self.path = '/interface/index.html'
            try:
                file_to_open = open(self.path[1:]).read()
                self.send_response(200)
            except:
                file_to_open = "File Not Found"
                self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes(file_to_open, 'utf-8'))
        elif self.path != '/favicon.ico':
            self.make_data()
    def make_data(self):
        parsed = urlparse(self.path)
        params = parse_qs(unquote(parsed.query))
        print(params)
        ret = model(params['text'])
        ret = list(ret.cpu().numpy()[0])
        body = json.dumps({"coord":[str(ret[0]),str(ret[1]),str(ret[2])]})
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Content-length', len(body.encode()))
        self.end_headers()
        self.wfile.write(body.encode())

httpd = HTTPServer(("", PORT), MyHandler)
print('serving at port:%s' % PORT)
httpd.serve_forever()