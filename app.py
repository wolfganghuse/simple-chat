from flask import Flask, render_template, request, jsonify, redirect
import requests
import argparse
import json

app = Flask(__name__)

def get_default_model_name(inference_host):
    kserve_url = f'http://{inference_host}/v1/models'
    torchserve_url = f'http://{inference_host}:8081/models'
    
    try:
        response = requests.get(kserve_url)
        response.raise_for_status()
        models = response.json()
        args.use_k8s = True
        print("Connected to kserve.")
        return models['models'][0]
    except Exception as e:
        print(f"Failed to connect to kserve at {kserve_url}: {e}")

    try:
        response = requests.get(torchserve_url)
        response.raise_for_status()
        models = response.json()
        args.use_k8s = False
        print("Connected to TorchServe.")
        return models['models'][0]['modelName']
    except Exception as e:
        print(f"Failed to connect to TorchServe at {torchserve_url}: {e}")

    print("Failed to fetch the default model name from both kserve and TorchServe.")
    return None

@app.route('/')
def index():
    if args.inference_host is None or args.model_name is None:
        return redirect('/connect')  # Redirect to /connect if no active connection
    return render_template('index.html')

@app.route('/connect', methods=['GET'])
def connect_form():
    return render_template('connect.html')

@app.route('/connect', methods=['POST'])
def connect():
    try:
        new_host = request.json.get('inference_host')
        if new_host:
            print(f"Attempting to connect to new inference host: {new_host}")
            
            # You might want to add validation for the new_host here
            
            args.inference_host = new_host
            print(f"New inference host set to: {new_host}")
            
            args.model_name = get_default_model_name(new_host)
            if args.model_name is None:
                raise Exception("Failed to get the default model name from the new inference host")
                
            print(f"Successfully fetched the default model name: {args.model_name}")
            
            return jsonify({'message': f'Successfully connected to {new_host} with model {args.model_name}'})
        else:
            print("Error: No inference host provided in the request")
            return jsonify({'error': 'No inference host provided'}), 400
    except Exception as e:
        print(f"Failed to connect to the new inference host: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask():
    if args.inference_host is None or args.model_name is None:
        return jsonify({'error': 'Please set the inference host and model name via /connect first'}), 400

    user_message = request.form['user_message']

    if args.use_k8s:
        model_endpoint = f'http://{args.inference_host}/v2/models/{args.model_name}/infer'
        payload = {
            "id": "1",
            "inputs": [
                {
                    "name": "input0",
                    "shape": [-1],
                    "datatype": "BYTES",
                    "data": [user_message]
                }
            ]
        }
        response = requests.post(model_endpoint, json=payload)
        result = response.json()
        reply = result['outputs'][0]['data']
        return jsonify({'model_response': reply})
    else:
        model_endpoint = f'http://{args.inference_host}:8080/predictions/{args.model_name}'
        response = requests.post(model_endpoint, data=user_message)
        if response.status_code == 200:
            return jsonify({'model_response': response.text})
        else:
            return jsonify({'model_response': 'Failed to get response from the model'})
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Chat Client for TorchServe')
    parser.add_argument('--model-name', help='The name of the model served by TorchServe', default=None)
    parser.add_argument('--inference-host', help='The host where the inference server is running', default='localhost')
    parser.add_argument('--use-k8s', help='Use kserve instead of torchserve', default=False)
    args = parser.parse_args()
    
    # if args.model_name is None:
    #     args.model_name = get_default_model_name(args.inference_host,args.use_k8s)
    #     if args.model_name is None:
    #         print("Please provide the model name or ensure that TorchServe/kserve is running with at least one model.")
    #         exit(1)

    # print(f"Using model: {args.model_name}")
    
    app.run(debug=True, host='0.0.0.0', port=8000)
