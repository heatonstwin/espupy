import plotly.graph_objs as go
from django.views.generic import ListView


class ListViewChartMixin(ListView):

    trace_type = None
    trace_name_field = None
    trace_x_field = None
    trace_y_field = None
    trace_options = None
    layout_title = None
    layout_x_axis_title = None
    layout_y_axis_title = None
    layout_options = None
    template_name_suffix = '_chart'

    def get_trace_options(self):
        return self.trace_options

    def get_layout_options(self):
        return self.layout_options

    def get_trace_name_field(self):
        return self.trace_name_field

    def get_x_data(self, name):
        queryset = self.get_queryset()
        fltr = {self.get_trace_name_field(): name}
        x_data = queryset.filter(**fltr).values_list(self.trace_x_field, flat=True)
        return x_data

    def get_y_data(self, name):
        queryset = self.get_queryset()
        fltr = {self.get_trace_name_field(): name}
        y_data = queryset.filter(**fltr).values_list(self.trace_y_field, flat=True)
        return y_data

    def get_trace(self):
        trace_options = self.get_trace_options()
        trace_obj = getattr(go, self.trace_type)
        trace = trace_obj(**trace_options or {})
        return trace

    def layout(self):
        layout_options = self.get_layout_options()
        layout = go.Layout(layout_options or {})
        return layout

