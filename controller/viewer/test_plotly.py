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

maxtime=30
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
@server.route("/update",methods=['POST'])
def update1():
    if not request.json:
        abort(400)
    nicetext=request.json
    print(nicetext)
    if(nicetext['type']=='cemon'):
        X1.append(nicetext['time'])
        Y1.append(nicetext['val'])
    elif(nicetext['type']=='nqmon'):
        X2.append(nicetext['time'])
        Y2.append(nicetext['val'])
    elif(nicetext['type']=='actual'):
        X3.append(nicetext['time'])
        Y3.append(nicetext['val'])
    return nicetext,201

@server.route("/hello",methods=['GET'])
def updat1():
    return 'hello world',200


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
    print('error cemon', error(v1,v3))
    print('error nqmon', error(v2,v3))
    # print("HH\n\n--------\n", X1,X2,X3,Y1,Y2,Y3)
    # print(trace1,trace2,trace3)
    return {'data': [trace1,trace2,trace3],
            'layout': go.Layout(
                xaxis=dict(range=[min([min(X1),min(X2),min(X3)]), max([max(X1),max(X2),max(X3)])]),
                yaxis=dict(range=[min([min(Y1),min(Y2),min(Y3)]), max([max(Y1),max(Y2),max(Y3)])]))
            }


if __name__=='__main__':
    app.run_server(debug=False)
