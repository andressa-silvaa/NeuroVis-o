#!/bin/bash
sudo apt-get update
sudo apt-get install -y unixodbc unixodbc-dev
pip install -r requirements.txt
python app.py