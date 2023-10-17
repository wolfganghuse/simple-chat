# Simple Chat client to communicate with local TorchServe instance

```
pip install -r requirements.txt
```

## Usage

```
python3 app.py
```

--use-k8s=True/False(default) switches to OIP Protocol for Inference. Needed for kserve

--inference-host=mpt.examplehost.com Default is localhost, can be used to connect to remote hosts

Model Type is auto-detected when connecting to Inference Host

