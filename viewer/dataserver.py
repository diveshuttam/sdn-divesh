from flask import Flask, request, abort

app = Flask(__name__)

@app.route("/update",methods=['POST'])
def update1():
    if not request.json:
        abort(400)
    nicetext=request.json
    print(nicetext['type'],nicetext['time'],nicetext['val'],sep=',')
    return nicetext,201

@app.route("/reset",methods=['POST'])
def reset():
    js=request.json
    print(f"***reseting,{js['alpha']},{js['delta']}")
    return 'done',200

@app.route("/reset_full",methods=['POST'])
def resetfull():
    js=request.json
    print('####reset_full')
    return 'done',200


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8050)