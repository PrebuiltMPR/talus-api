import shlex
import subprocess

import flask
import requests
from dotenv import dotenv_values
from flask import Flask, abort, request

MPR_URL = "https://mpr.hunterwittenborn.com/packages-meta-ext-v1.json.gz"
MPR_README = "https://raw.githubusercontent.com/PrebuiltMPR/builder/master/README.md"
README_LIMITER = '| :-----------: | ------------: |'

KEYS: dict = dotenv_values(".env")

def get_badge_url(package: str) -> str:
    return 'https://github.com/PrebuiltMPR/builder/actions/workflows/'+package+'.yml/badge.svg'

def is_valid_package(package: str) -> bool:
    resp = requests.get(MPR_URL)
    paklist = resp.json()
    all_packages = [ x["Name"] for x in paklist ]

    if package in all_packages:
        return True
    else:
        return False

def get_mpr_package_list() -> list:
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

def is_in_prebuildMPR(package: str) -> bool:
    mpr_packages = get_mpr_package_list()
    
    if package in mpr_packages:
        return True
    else:
        return False

def gen_response(success: bool, message) -> dict:
    return {
            'status': "success" if success else "failed",
            'message': message
        }

app = Flask(__name__)

@app.route("/add/", methods=['GET'])
def exec_add():
    command = 'bash addtorepo.sh '
    print("============")
    package = request.args.get('package')
    key = request.args.get('apikey')
    if key not in KEYS.values():
        abort(401)
    
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
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    output, err = process.communicate()
    print("Run successfully")
    return flask.jsonify( gen_response(True, 'Added package ' + package) )

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
