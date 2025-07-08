from flask import Flask, request
import sys
import json

app = Flask(__name__)

@app.route('/enqueue/alert', methods=['POST'])
def log_alert():
    data = request.get_json(force=True, silent=True)
    print("\n--- Received Alert ---", file=sys.stdout)
    print(json.dumps(data, indent=2), file=sys.stdout)
    sys.stdout.flush()
    return {'status': 'received'}, 200

@app.route('/', methods=['GET'])
def health():
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080) 