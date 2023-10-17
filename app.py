from flask import Flask, render_template, request, jsonify
import requests
import argparse

app = Flask(__name__)

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
    parser.add_argument('--model-name', required=True, help='The name of the model served by TorchServe')
    parser.add_argument('--inference-host', default='localhost', help='The host where the inference server is running')
    args = parser.parse_args()
    
    app.run(debug=True, host='0.0.0.0', port=8000)
