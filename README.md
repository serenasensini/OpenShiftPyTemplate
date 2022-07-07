# OpenShift--PyTemplating

# Synopsis

Py script to write an OpenShift template using a simple wizard through the CLI. This will produce a template in YAML and JSON format.

# Demo

![OpenShiftPyTemplate-–-template yaml-2022-06-16-18-29-15-_online-video-cutter com_](https://user-images.githubusercontent.com/17291035/174121629-6829965d-f384-4317-a381-7946ae79b4cd.gif)

# Installation

Only for Python 3.x.

Just run: 

```
pip install -r requirements.txt
python3 main.py
```

# Available objects

- DeploymentConfig
- Route
- Service (ClusterIP)
- ConfigMap
- Secret
- PVC
- Imagestream 
- Deployment
- PV

# TODO

Add:
- Service (NodePort, ExternalName)
- StatefulSet
- Build
- BuildConfig

Enhance:
- DeploymentConfig Configuration with ENV and commands properties
