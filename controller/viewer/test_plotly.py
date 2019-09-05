import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
from collections import deque
from datetime import datetime

X1 = deque(maxlen=40)
X1.append(datetime.now())
Y1 = deque(maxlen=40)
Y1.append(0)

X2 = deque(maxlen=40)
X2.append(datetime.now())
Y2 = deque(maxlen=40)
Y2.append(0)



X3 = deque(maxlen=300)
X3.append(datetime.now())
Y3 = deque(maxlen=300)
Y3.append(0)

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

app = dash.Dash(__name__)
app.layout = html.Div(
    [
        dcc.Graph(id='live-graph',
                  animate=True,
                  figure={'data': [initial_trace1,initial_trace2, initial_trace3],
                          'layout': go.Layout(
                                xaxis=dict(range=[max([min(X1),min(X2),min(X3)]), min([max(X1),max(X2),max(X3)])]),
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
    # from random import randint
    # X1.append(datetime.now().timestamp())
    # Y1.append(randint(1,10))

    # X2.append(datetime.now().timestamp()+randint(0,1))
    # Y2.append(randint(1,10))
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

    print(trace1.y,trace2.y,trace3.y)
    return {'data': [trace1,trace2,trace3],
            'layout': go.Layout(
                xaxis=dict(range=[max([min(X1),min(X2),min(X3)]), min([max(X1),max(X2),max(X3)])]),
                yaxis=dict(range=[min([min(Y1),min(Y2),min(Y3)]), max([max(Y1),max(Y2),max(Y3)])]))
            }

def update1(x1,y1):
    X1.append(x1)
    Y1.append(y1)

def update2(x2,y2):
    X2.append(x2)
    Y2.append(y2)

def update3(x3,y3):
    X3.append(x3)
    Y3.append(y3)

if __name__ == '__main__':
    from random import randint
    import time
    for i in range(10):
        update1(datetime.now().timestamp(),randint(0,10))
        time.sleep(0.1)
    app.run_server(port=8051, debug=True)