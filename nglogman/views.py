import os
import re
import itertools

from django.template import loader
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response
from django.contrib import messages
from django.db.models import Count, Q

import pandas as pd
import uuid
from datetime import timedelta

from bokeh.layouts import column
from bokeh.plotting import figure
from bokeh.embed import components


from . models import Task, LGNode, NodeGroup
from nglm_grpc.gRPCMethods import setConfig, ROOT_DIR, getConfig, checkNodes
from nglm_grpc.modules.Utility import acronymTitleCase

def searchView(request):
    template = loader.get_template('search.html')


def TaskListView(request):
    template = loader.get_template('tasks.html')
    context = {
        'task_set': Task.objects.exclude(status='Completed'),
        'scheduled_tasks': Task.objects.filter(status='Scheduled'),
        'in_progress': Task.objects.filter(status='In Progress'),
        'completed_tasks': Task.objects.filter(status='Completed'),
        'failed_tasks': Task.objects.filter(status__contains='Failed')
    }
    return HttpResponse(template.render(context, request))


def DashboardView(request):
    template = loader.get_template('dashboard.html')
    context = {
        'node_groups': NodeGroup.objects.all().annotate(
            node_count=Count('nodes')
        ),
        'available_node_set': LGNode.objects.filter(status='Available'),
        'task_set': Task.objects.exclude(status='Completed')
    }
    return HttpResponse(template.render(context, request))


def outputDownload(request, document_root, path=''):
    filePath = os.path.join(document_root, path)
    with open(filePath, 'rb') as f:
        response = HttpResponse(f.read())
        response['content_type'] = 'application/vnd.ms-excel'
        response['Content-Disposition'] = 'attachment;filename=' + path
        return response


def GroupListView(request):
    template = loader.get_template('groups.html')
    if request.GET.get('refresh'):
        print('checking nodes...')
        checkNodes(LGNode.objects.all())
        return redirect('groups')
    context = {
        'node_groups': NodeGroup.objects.all().annotate(
            node_count=Count('nodes'),
            off_count=Count('nodes', filter=Q(nodes__status__iexact='offline'))
        )
    }
    return HttpResponse(template.render(context, request))


def NodeListView(request):
    if request.GET.get('refresh'):
        print('checking nodes...')
        checkNodes(LGNode.objects.all())
        return redirect('nodes')
    template = loader.get_template('nodes.html')
    context = {
        'available_node_set': LGNode.objects.exclude(status='Offline'),
        'offline_node_set': LGNode.objects.filter(status='Offline')
    }
    return HttpResponse(template.render(context, request))


def ConfigUpload(request, groupID=''):
    from .forms import ConfigForm
    template = loader.get_template('config.html')
    getConfig(NodeGroup.objects.get(id=groupID).nodes.all())
    if request.method == 'POST':
        form = ConfigForm(groupID, request.POST, request.FILES)
        if form.is_valid():
            failedNodes = setConfig(
                NodeGroup.objects.get(id=groupID).nodes.all(),
                request.FILES['file'])
            if not failedNodes:
                messages.success(request, 'Successfully set all configs.')
            else:
                messages.warning(request, 'Failed to set config for: '
                                 + ', '.join(failedNodes))
    else:
        form = ConfigForm(groupID)
    context = {
        'form': form,
        'group_name': NodeGroup.objects.get(id=groupID).groupname,
        'all_nodes': NodeGroup.objects.get(id=groupID).nodes.all(),
        'offline_nodes': NodeGroup.objects.get(id=groupID).nodes.filter(
            status__iexact="offline"
        )
    }
    return HttpResponse(template.render(context, request))

def overviewGraph(request, taskUUID=''):
    template = loader.get_template('overview.html')
    task = Task.objects.get(taskUUID=uuid.UUID(taskUUID))
    xlsx = pd.ExcelFile(os.path.join(
        ROOT_DIR, "Reports", task.taskName + '_' + taskUUID,
        str(task.startTime), 'overview.xlsx'))
    dfs = pd.read_excel(xlsx, sheet_name=None)
    full_df = pd.DataFrame()
    for name, sheet in dfs.items():
        sheet['node'] = name
        full_df = full_df.append(sheet)

    figures = list()
    statlines = dict()
    full_df.columns = full_df.columns.str.replace(r'\s+', '_')
    tooltips = [('(x, y)', '($x{int}, $y)')]
    for col in full_df:
        if col == 'Time' or col == 'node':
            continue

        plot = figure(
            width=1000, height=300,
            x_axis_label='Time Elapsed (s)',
            y_axis_label=acronymTitleCase(col.replace('_', ' ')),
            title=acronymTitleCase(col.replace('_', ' ')),
            sizing_mode='stretch_both',
            tooltips=tooltips
        )
        plot.title.text_font_size = '14pt'
        plot.title.text_font_style = 'bold'

        data = dict()

        for row in full_df.itertuples():
            if not re.search('[a-z]', row.Time):
                if not data.get(row.node):
                    data[row.node] = [list(), list()]
                data[row.node][0].append(row.Index * task.interval)
                data[row.node][1].append(getattr(row, col))
            # else:
            #     if not statlines.get(row.Time):
            #         statlines[row.Time] = list()
            #     statlines[row.Time].append(plot.line(
            #         row.Index, col, line_dash='dashed', visible=False))

        if(len(data.items()) <= 10):
            from bokeh.palettes import Category10_10 as palette
        else:
            from bokeh.palettes import Category20_20 as palette

        colors = itertools.cycle(palette)
        for node, val in data.items():
            y_average = [sum(val[1]) / len(val[1])] * len(val[1])
            color = next(colors)
            plot.line(val[0], val[1], legend=node, color=color,
                      line_width=2)
            plot.line(val[0], y_average,
                      line_dash='dashed', color=color)
    #        plot.circle(val[0], val[1], fill_color="white", color=color,
    #                    size=8)
        plot.legend.click_policy = "hide"
        figures.append(plot)

    figures = column(*figures)
    # opts = [key for key in statlines].insert(0, 'None')
    # select = Select(title='Statline:', value='None', options=opts)
    # select.callback = CustomJS(args=statlines, code="""
    #
    # """)
    script, div = components(figures)
    context = {'bokehScript': script, 'bokehDiv': div}
    return HttpResponse(template.render(context, request))
