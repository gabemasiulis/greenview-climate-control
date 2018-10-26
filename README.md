# Greenview Climate Control
### Introduction
An app that consists of a central Flask server that receives data from nodeMCU/DHT11 powered sensors
that are placed strategically in a home, to record temperature differentials.
### Development
1. Clone this repository
2. Initialize a virtual environment `python3 -m venv venv`
3. Activate the virtual environment `. venv/bin/activate`
4. Install necessary pip packages `pip3 install -r requirements.txt`
5. Define flask's environment variable `export FLASK_APP=app.py`
6. `flask run`