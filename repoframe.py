from nicegui import app,ui
from utility import logNavigate, setBackgroud, protectPage, getEpochRange, \
                        generate_date_range, get_period, fromEpochToDatetime
from header import header
from footer import footer
import dbutils
from constants import COLORS, MONTHS, YEARS
from tasks import findTask, _tasks
from customers import CustomersManager
 

@ui.page('/repoframe/')
def repoframe_page():

    CONTROLS={}

    def buildCalHeatMap(year, title, data, tab, method):
        options = {
            'title': { 'top': 30, 'left': 'center', 'text': title },
            'tooltip': {},
            'visualMap': { 'min': 0.0, 'max': 16.0, 'type': 'piecewise', 'orient': 'horizontal',
                            'left': 'center', 'top': 65 },
            'calendar': { 'top': 120, 'left': 30, 'right': 30, 'cellSize': ['auto', 40, 40],
                            'range': year, 'itemStyle': { 'borderWidth': 0.5 },
                            'yearLabel': { 'show': False }},
            'series': { 'type': 'heatmap', 'coordinateSystem': 'calendar', 'data': data }
            }
        if method=='create':
            echart = ui.echart(options)
            echart.classes('h-full')
        else :
            # CONTROLS[tab]['chart'].options['series'] = options['series']
            # CONTROLS[tab]['chart'].update()
            CONTROLS[tab]['chart'].parent_slot.parent.remove(CONTROLS[tab]['chart'])
            echart = ui.echart(options)
            echart.classes('h-full')
            CONTROLS[tab]['chart']=echart
        return echart

    def buildPie(data, title, tab, method):
        options={
                'tooltip': {'trigger': 'item',
                            ':formatter': """
                                function (params) {
                                    const seconds = params.value;
                                    const hours = Math.floor(seconds / 3600);
                                    const minutes = Math.floor((seconds % 3600) / 60);
                                    return `${params.name}: ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
                                    }
                                    """
                            },
                'legend': {'orient': 'vertical', 'left': 'right'},
                'series': [
                    {'name': title,'type': 'pie','radius': ['30%', '100%'],
                        'left':'0%', 'top': '0%', 'right':'0%', 'bottom':'0%',
                        'avoidLabelOverlap': False,'padAngle': 5,
                        'itemStyle': {'borderRadius': 10},'label': {'show': False,'position': 'center'},
                        'emphasis': {'label': {'show': True,'fontSize': 24,'fontWeight': 'bold'}},
                        'labelLine': {'show': True},
                        'data': data
                    }]
                }
        if method=='create':
            echart = ui.echart(options)
            echart.classes('h-full')
        else :
            CONTROLS[tab]['chart'].options['series'] = options['series']
            CONTROLS[tab]['chart'].update()
            return None
        return echart

    def buildToggles(onlyYears=False):
        elements={}

        with ui.column():
            with ui.row():
                elements['year']=ui.toggle(YEARS, value=YEARS[0])
                elements['switch'] = ui.switch('Months')
                elements['switch'].set_value(True)
            elements['month']=ui.toggle(MONTHS, value='Jan').bind_visibility_from(elements['switch'], 'value')
        if onlyYears:
            elements['switch'].set_value(False)
            elements['switch'].set_visibility(False)
        return elements


    def refresh(mode):
        year=CONTROLS[mode]['toggles']['year'].value
        if CONTROLS[mode]['toggles']['switch'].value:
            month=MONTHS[CONTROLS[mode]['toggles']['month'].value]
        else:
            month=''
        (fromepoch, toepoch)=getEpochRange(year, month)
        if mode=='one':
            dbdata=dbutils.taskDB.read_stats_by_customer(fromepoch, toepoch, user=app.storage.user.get('username', ''))
        elif mode=='two':
            dbdata=dbutils.taskDB.read_stats_by_tag(fromepoch, toepoch, user=app.storage.user.get('username', ''))
        elif mode in ['three', 'four']:
            (begin_date, end_date)= get_period(CONTROLS[mode]['toggles']['switch'].value, CONTROLS[mode]['toggles']['year'].value,
                         MONTHS[CONTROLS[mode]['toggles']['month'].value] )
            date_range=generate_date_range(begin_date, end_date)
            dbdata=dbutils.taskDB.read_stats_by_day_month(fromepoch, toepoch, user=app.storage.user.get('username', ''))
        else:
            return
        
        if mode in ['one', 'two']:
           # Process dbdata to build the UI data structure
            data=[{'value': el[0], 'name': el[1]} for el in dbdata]

        elif mode in ['three']:
            if len(month):
                # Process dbdata to build the UI data structure ( month case )
                date_dict={}
                for el in date_range:
                    date_dict[el]=0
                for el in dbdata:
                    (date,_)=fromEpochToDatetime(el[1])
                    date_dict[date]+=el[0]
                data=[{'value': date_dict[el], 'name': el} for el in date_dict]
            else:
                # Process dbdata to build the UI data structure ( year case )
                date_dict={}
                for el in MONTHS:
                    date_dict[year+'-'+MONTHS[el]]=0
                for el in dbdata:
                    (date,_)=fromEpochToDatetime(el[1])
                    date_dict[date[:7]]+=el[0]
                data=[{'value': date_dict[el], 'name': el} for el in date_dict]
        elif mode in ['four']:
            # Process dbdata to build the UI data structure ( month case )
            date_dict={}
            for el in date_range:
                date_dict[el]=0
            for el in dbdata:
                (date,_)=fromEpochToDatetime(el[1])
                date_dict[date]+=el[0]
            data=[[el, date_dict[el]/3600] for el in date_dict]

        if mode in ['one', 'two', 'three']:
            # remove previous chart if created
            if 'chart' in CONTROLS[mode]:
                buildPie(data, 'Time spent on Customers', mode, 'update')
            else:
                # build new chart
                CONTROLS[mode]['chart']=buildPie(data, 'Time spent on Customers', mode, 'create')
        else:
            # remove previous chart if created
            if 'chart' in CONTROLS[mode]:
                buildCalHeatMap(year, f'Time in {year}', data, mode, 'update')
            else:
                # build new chart
                CONTROLS[mode]['chart']=buildCalHeatMap(year, f'Time in {year}', data, mode, 'create')


        return

    if protectPage(app.storage.user.get('authenticated', False)):
        logNavigate('/login/')
        return
    
    header()
    setBackgroud()
    GEN_CLASSES=f'{COLORS['Ready']} w-full h-full'
    with ui.tabs().classes(GEN_CLASSES) as tabs:
        one = ui.tab('By Customers')
        two = ui.tab('By Tag')
        three = ui.tab('By Day/Month')
        four = ui.tab('Heatmap')
    with ui.tab_panels(tabs, value=one).classes(GEN_CLASSES) as tab_panels:
        tab_panels.style('height: calc(100vh - 14rem)')
        with ui.tab_panel(one).classes(GEN_CLASSES):
            ui.label('Report by Customers')
            CONTROLS['one']={}
            CONTROLS['one']['toggles']=buildToggles()
            CONTROLS['one']['refresh']=ui.button('Refresh', on_click=lambda: refresh('one'))
        with ui.tab_panel(two).classes(GEN_CLASSES):
            ui.label('Report by Tag')
            CONTROLS['two']={}
            CONTROLS['two']['toggles']=buildToggles()
            CONTROLS['two']['refresh']=ui.button('Refresh', on_click=lambda: refresh('two'))
        with ui.tab_panel(three).classes(GEN_CLASSES):
            ui.label('Report by Day/Month')
            CONTROLS['three']={}
            CONTROLS['three']['toggles']=buildToggles()
            CONTROLS['three']['refresh']=ui.button('Refresh', on_click=lambda: refresh('three'))
        with ui.tab_panel(four).classes(GEN_CLASSES):
            ui.label('Heatmap')
            CONTROLS['four']={}
            CONTROLS['four']['toggles']=buildToggles(onlyYears=True)
            CONTROLS['four']['refresh']=ui.button('Refresh', on_click=lambda: refresh('four'))
    footer()