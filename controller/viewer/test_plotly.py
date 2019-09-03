import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
from collections import deque
from datetime import datetime

X1 = deque(maxlen=20)
X1.append(datetime.now().timestamp())
Y1 = deque(maxlen=20)
Y1.append(1)

X2 = deque(maxlen=20)
X2.append(datetime.now().timestamp())
Y2 = deque(maxlen=20)
Y2.append(1)


initial_trace1 = plotly.graph_objs.Scatter(
    x=list(X1),
    y=list(Y1),
    name='Scatter1',
    mode='lines+markers'
)

initial_trace2 = plotly.graph_objs.Scatter(
    x=list(X2),
    y=list(Y2),
    name='Scatter2',
    mode='lines+markers'
)

app = dash.Dash(__name__)
app.layout = html.Div(
    [
        dcc.Graph(id='live-graph',
                  animate=True,
                  figure={'data': [initial_trace1,initial_trace2],
                          'layout': go.Layout(
                              xaxis=dict(range=[min([min(X1),min(X2)]), max(max(X1),max(X2))]),
                              yaxis=dict(range=[min([min(Y1),min(Y2)]), max(max(Y1),max(Y2))])
                          )
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
    from random import randint
    X1.append(datetime.now().timestamp())
    Y1.append(randint(1,10))

    X2.append(datetime.now().timestamp()+randint(0,1))
    Y2.append(randint(1,10))
    trace1 = plotly.graph_objs.Scatter(
        x=list(X1),
        y=list(Y1),
        name='Scatter',
        mode='lines+markers'
    )

    trace2 = plotly.graph_objs.Scatter(
        x=list(X2),
        y=list(Y2),
        name='Scatter',
        mode='lines+markers'
    )

    return {'data': [trace1,trace2],
            'layout': go.Layout(
                xaxis=dict(range=[min([min(X1),min(X2)]), max(max(X1),max(X2))]),
                yaxis=dict(range=[min([min(Y1),min(Y2)]), max(max(Y1),max(Y2))]))
            }


if __name__ == '__main__':
    app.run_server(port=8051, debug=True)