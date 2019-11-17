import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
from collections import deque
from datetime import datetime
from threading import Lock
from flask import Flask, request, abort
from error import error

maxtime=60
server = Flask(__name__)
lock1 = Lock()
lock2 = Lock()
lock3 = Lock()
print('------------------------importing plotly----------------------------------------')
X1 = deque()
X1.append(0)
Y1 = deque()
Y1.append(0)

X2 = deque()
X2.append(0)
Y2 = deque()
Y2.append(0)



X3 = deque()
X3.append(0)
Y3 = deque()
Y3.append(0)

init1 = True
init2 = True
init3 = True

min_err_n = None
max_err_n = None
avg_err_n = None
count_err_n = 0
sum_err_n = 0

min_err_c = None
max_err_c = None
avg_err_c = None
count_err_c = 0
sum_err_c = 0

@server.route("/update",methods=['POST'])
def update1():
    if not request.json:
        abort(400)
    nicetext=request.json
    print(nicetext)
    if(nicetext['type']=='cemon'):
        X1.append((nicetext['time']))
        Y1.append(nicetext['val'])
    elif(nicetext['type']=='nqmon'):
        X2.append(nicetext['time'])
        Y2.append(nicetext['val'])
    elif(nicetext['type']=='actual'):
        X3.append(nicetext['time'])
        Y3.append(nicetext['val'])
    return nicetext,201

def reset():
    global X1
    global Y1
    
    global X2
    global Y2

    global X3
    global Y3

    global init1
    global init2
    global init3

    X1 = deque()
    X1.append(0)
    Y1 = deque()
    Y1.append(0)

    X2 = deque()
    X2.append(0)
    Y2 = deque()
    Y2.append(0)



    X3 = deque()
    X3.append(0)
    Y3 = deque()
    Y3.append(0)

    global min_err_n
    global max_err_n
    global avg_err_n
    global count_err_n
    global sum_err_n

    global min_err_c
    global max_err_c
    global avg_err_c
    global count_err_c
    global sum_err_c

    min_err_n = None
    max_err_n = None
    avg_err_n = None
    count_err_n = 0
    sum_err_n = 0

    min_err_c = None
    max_err_c = None
    avg_err_c = None
    count_err_c = 0
    sum_err_c = 0

    init1 = True
    init2 = True
    init3 = True

@server.route("/reset",methods=['POST'])
def updat1():
    reset()
    js=request.json
    print(f"reseting {js['alpha'], js['delta']}")
    return 'done',200


initial_trace1 = plotly.graph_objs.Scatter(
    x=list(X1),
    y=list(Y1),
    name='CeMon',
    mode='lines+markers'
)

initial_trace2 = plotly.graph_objs.Scatter(
    x=list(X2),
    y=list(Y2),
    name='NqMon',
    mode='lines+markers'
)

initial_trace3 = plotly.graph_objs.Scatter(
    x=list(X3),
    y=list(Y3),
    name='Actual',
    mode='lines+markers'
)

app = dash.Dash(__name__,server=server)

app.layout = html.Div(
    [
        dcc.Graph(id='live-graph',
                  animate=True,
                  figure={'data': [initial_trace1,initial_trace2, initial_trace3],
                          'layout': go.Layout(
                                xaxis=dict(range=[min([min(X1),min(X2),min(X3)]), max([max(X1),max(X2),max(X3)])]),
                                yaxis=dict(range=[min([min(Y1),min(Y2),min(Y3)]), max([max(Y1),max(Y2),max(Y3)])]))
                          }),
        dcc.Interval(
            id='graph-update',
            interval=1*1000
        ),
    ]
)





@app.callback(Output('live-graph', 'figure'),
              [Input('graph-update', 'n_intervals')])
def update_graph_scatter(n):
    while(abs(X1[0]-X1[-1])>maxtime):
        X1.popleft()
        Y1.popleft()
    while(abs(X2[0]-X2[-1])>maxtime):
        X2.popleft()
        Y2.popleft()
    while(abs(X3[0]-X3[-1])>maxtime):
        X3.popleft()
        Y3.popleft()

    trace1 = plotly.graph_objs.Scatter(
        x=list(X1),
        y=list(Y1),
        name='CeMon',
        mode='lines+markers'
    )

    trace2 = plotly.graph_objs.Scatter(
        x=list(X2),
        y=list(Y2),
        name='NqMon',
        mode='lines+markers'
    )

    trace3 = plotly.graph_objs.Scatter(
        x=list(X3),
        y=list(Y3),
        name='Actual',
        mode='lines+markers'
    )

    v1 = list(zip(X1,Y1))
    v2 = list(zip(X2,Y2))
    v3 = list(zip(X3,Y3))

    ce = error(v1,v3)
    ne = error(v2,v3)

    global min_err_n
    global max_err_n
    global avg_err_n
    global count_err_n
    global sum_err_n

    global min_err_c
    global max_err_c
    global avg_err_c
    global count_err_c
    global sum_err_c

    if(min_err_c==None):
        min_err_c=max_err_c=ce
    if(min_err_n==None):
        min_err_n=max_err_n=ne

    if(ne!=None):
        min_err_n=min(min_err_n,ne)
        max_err_n=max(max_err_n,ne)
        count_err_n+=1
        sum_err_n+=ne
        avg_err_n=sum_err_n/count_err_n
    if(ce!=None):
        min_err_c=min(min_err_c,ce)
        max_err_c=max(max_err_c,ce)
        sum_err_c+=ce
        count_err_c+=1
        avg_err_c=sum_err_c/count_err_c

    print('\n***error nemon', ne,  min_err_n, max_err_n, avg_err_n)
    print('\n***error cqmon', ce,  min_err_c, max_err_c, avg_err_c)
    # print("HH\n\n--------\n", X1,X2,X3,Y1,Y2,Y3)
    # print(trace1,trace2,trace3)
    yrange = [min([min(Y1),min(Y2),min(Y3)]), max([max(Y1),max(Y2),max(Y3)])]
    if(yrange[0]==yrange[1]):
        yrange[0]-=1
        yrange[1]+=1
    return {'data': [trace1,trace2,trace3],
            'layout': go.Layout(
                xaxis=dict(range=[min([min(X1),min(X2),min(X3)]), max([max(X1),max(X2),max(X3)])]),
                yaxis=dict(range=yrange))
            }


if __name__=='__main__':
    app.run_server(host='0.0.0.0',port =8050, debug=False)
