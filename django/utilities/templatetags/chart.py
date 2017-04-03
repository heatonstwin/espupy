from django import template

import plotly
import plotly.graph_objs as go


register = template.Library()


def parse_args(args):
    items = [item.split('=') for item in args.split(',')]
    return {item[0].strip(): item[1].strip() for item in items}


def plot(parser, token):
    tag_name, arg = token.contents.split(None, 1)
    arg = parse_args(arg)
    return PlotNode(**arg)


class PlotNode(template.Node):

    def __init__(self, height, width):
        self.object_list = template.Variable('object_list')
        self.height = height
        self.width = width

    def render(self, context):
        object_list = self.object_list.resolve(context)
        view = context['view']

        trace_names = object_list.values_list(view.get_trace_name_field(),
                                              flat=True)
        names = list(set(trace for trace in trace_names))

        traces = []
        for name in names:
            trace = view.get_trace()
            trace.name = name
            x_data = view.get_x_data(name=name)
            y_data = view.get_y_data(name=name)
            trace.x = [x for x in x_data]
            trace.y = [y for y in y_data]
            traces.append(trace)

        layout = view.layout()
        layout.height = self.height
        layout.width = self.width
        figure = dict(data=traces, layout=layout)
        plot_div = plotly.offline.plot(figure, output_type='div')
        return plot_div


register.tag('plot_div', plot)
