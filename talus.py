from flask import Flask
from flask import request
import flask
from flask import abort
import requests
import subprocess
import shlex
import urllib.parse
import pipes
import dotenv
dotenv.load_dotenv()
import os

app = Flask(__name__)

MPR_URL = "https://mpr.hunterwittenborn.com/packages-meta-ext-v1.json.gz"
MPR_README = "https://raw.githubusercontent.com/PrebuiltMPR/builder/master/README.md"
README_LIMITER = '| :-----------: | ------------: |'

keys = {
  'leo': os.getenv("LEO_KEY"),
  'mpr': os.getenv("MPR_KEY")
}

def get_badge_url(package):
    return 'https://github.com/PrebuiltMPR/builder/actions/workflows/'+package+'.yml/badge.svg'

def is_valid_package(package):
    resp = requests.get(MPR_URL)
    paklist = resp.json()
    all_packages = [ x["Name"] for x in paklist ]

    if package in all_packages:
        return True
    else:
        return False

def get_mpr_package_list():
    mpr_packages = list()

    resp = requests.get(MPR_README)
    data = resp.text.splitlines()

    for i, line in enumerate(data):
        if line == README_LIMITER:
            for line in data[i+1:]:
                p = line.split("|")[1].strip()
                mpr_packages.append(p)
            break

    return mpr_packages

def is_in_prebuildMPR(package):
    mpr_packages = get_mpr_package_list()
    
    if package in mpr_packages:
        return True
    else:
        return False

def gen_response(success, message):
    return {
            'status': "success" if success else "failed",
            'message': message
        }

@app.route("/add/", methods=['GET'])
def exec_add():
    command = '/bin/bash /home/talus/addtorepo.sh '
    print("============")
    package = request.args.get('package')
    key = request.args.get('apikey')
    if key not in keys.values():
        abort(401)
    
    if request.method == 'GET':
        print('Checking package validity')
        pack = package.split()[0]

        if is_valid_package(pack):
            print('Requested package is valid.')
        else:
            print('Requested package is invalid. ABORT')
            return flask.jsonify( gen_response(False, "Requested package does not exist") )

        if is_in_prebuildMPR(pack):
            print('Requested package does already exist')
            return flask.jsonify( gen_response(False, "Requested package does already exist in PrebuiltMPR") )

        print('Started executing command')
        command = shlex.split(command + pack)
        process = subprocess.Popen(command, stdout = subprocess.PIPE)
        print("Run successfully")
        output, err = process.communicate()
        return flask.jsonify( gen_response(True, 'Added package ' + package) )
    return "not executed"

@app.route("/list/", methods=["GET"])
def exec_list():
    print("============")
    paklist = get_mpr_package_list()
    return flask.jsonify( gen_response(True, paklist) )

@app.route("/badge/", methods=["GET"])
def exec_badge():
    package = request.args.get('package')
    if is_in_prebuildMPR(package):
        return flask.jsonify( gen_response(True, get_badge_url(package)) )
    else:
        return flask.jsonify( gen_response(False, "Requested badge does not exist") )

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')
