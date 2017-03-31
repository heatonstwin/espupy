from django import template

import plotly
import plotly.graph_objs as go


register = template.Library()


def plot(parser, token):
    return PlotNode()


class PlotNode(template.Node):

    def __init__(self):
        self.object_list = template.Variable('object_list')

    def render(self, context):
        object_list = self.object_list.resolve(context)
        one = [obj for obj in object_list][0]

        chart = go.Scatter(
            x=[obj.timestamp for obj in object_list],
            y=[obj.measurement for obj in object_list],
            name=one.sensor.device.model,
            mode='lines',
            line=dict(color='#0F86DB', width=2)
        )
        layout = dict(
            title=one.sensor.device.model,
            xaxis=dict(title='Timestamp'),
            yaxis=dict(title='Measurement ({})'.format(one.unit)),
            height=600
        )
        figure = dict(data=[chart], layout=layout)
        plot_div = plotly.offline.plot(figure, output_type='div')
        return plot_div


register.tag('plot_div', plot)
