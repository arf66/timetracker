from nicegui import app,ui
from utility import logNavigate, setBackgroud, protectPage, getEpochRange
from header import header
from footer import footer
import dbutils
from constants import COLORS, MONTHS, YEARS
from tasks import findTask, _tasks
from customers import CustomersManager
 

@ui.page('/repoframe/')
def repoframe_page():

    CONTROLS={}


    def buildPie(data, title, tab, method):
        options={
                'tooltip': {'trigger': 'item'},
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

    def buildToggles():
        elements={}

        with ui.column():
            with ui.row():
                elements['year']=ui.toggle(YEARS, value=YEARS[0])
                elements['switch'] = ui.switch('Months')
                elements['switch'].set_value(True)
            elements['month']=ui.toggle(MONTHS, value='Jan').bind_visibility_from(elements['switch'], 'value')
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
        else:
            return
        
        # Process dbdata to build the UI data structure
        data=[{'value': el[0], 'name': el[1]} for el in dbdata]

        # remove previous chart if created
        if 'chart' in CONTROLS[mode]:
            buildPie(data, 'Time spent on Customers', mode, 'update')
        else:
            # build new chart
            CONTROLS[mode]['chart']=buildPie(data, 'Time spent on Customers', mode, 'create')
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
    footer()