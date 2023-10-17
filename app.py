from flask import Flask, render_template, request, jsonify
import requests
import argparse
import json

app = Flask(__name__)

def get_default_model_name(inference_host):
    try:
        response = requests.get(f'http://{inference_host}:8081/models')
        response.raise_for_status()
        models = response.json()
        # Returning the first model name as default
        return models['models'][0]['modelName']
    except Exception as e:
        print(f"Failed to fetch the default model name from TorchServe: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_message = request.form['user_message']
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
    args = parser.parse_args()
    
    if args.model_name is None:
        args.model_name = get_default_model_name(args.inference_host)
        if args.model_name is None:
            print("Please provide the model name or ensure that TorchServe is running with at least one model.")
            exit(1)

    print(f"Using model: {args.model_name}")
    
    app.run(debug=True, host='0.0.0.0', port=8000)
