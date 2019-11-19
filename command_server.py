import subprocess
from flask import Flask, request

app = Flask(__name__)
current_process = None

@app.route("/run",methods=['POST'])
def update():
    try:
        global current_process
        if(current_process!=None):
            current_process.kill()
        js = request.json
        print('running', js['command'])
        current_process = subprocess.Popen(js['command'])
        print('returning done')
        return "Done",201
    except:
        print('returning not done')
        return "NotDone", 201

if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000)