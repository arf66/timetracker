from nicegui import app,ui
from utility import logNavigate, setBackgroud, protectPage, getEpochRange, \
                        generate_date_range, get_period, fromEpochToDatetime, secsToHHMM
from header import header
from footer import footer
import dbutils
from constants import COLORS, MONTHS, YEARS, TAGS
from tasks import findTask, _tasks
from customers import CustomersManager
from datetime import datetime
import os
import tempfile
import csv


class ToggleButton(ui.button):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._state = True
        self.on('click', self.toggle)

    def toggle(self) -> None:
        """Toggle the button state."""
        self._state = not self._state
        self.update()

    def update(self) -> None:
        self.props(f'color={"green" if self._state else "red"}')
        super().update()

@ui.page('/admin/')
def repoadmin_page():

    CONTROLS={}

    def export_table_to_csv(mode):
        # get the right structure of the data
        header_names = [col['headerName'] for col in CONTROLS[mode]['columns']]

        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            filename = tmp_file.name
            # Write data to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Write header
                writer.writerow(header_names)
                # Write rows
                for row in CONTROLS[mode]['rows']:
                    if mode=='two':
                        writer.writerow( \
                            [row['User'], row['Tag'], row['Duration']])
                    elif mode=='three':
                        writer.writerow( \
                            [row['user'], row['day'], row['task'], row['tag'], row['customer'], row['duration']])
                        
            # Trigger download in NiceGUI
            ui.download.file(filename)


    def get_month_name_from_value(month_value):
        # Iterate over the dictionary items
        for month_name, number in MONTHS.items():
            if number == month_value:
                return month_name
        return None 

    def get_current_year_and_month():
        # Get the current date
        now = datetime.now()
        
        # Format year and month
        year = now.strftime("%Y")
        month = now.strftime("%m")
        
        # Return as a tuple
        return year, month


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

    
    def buildColumnsUserTag():
        return [
            {'headerName': 'User', 'label': 'User', 'field': 'User', 'required': True, 'align': 'left', 
                'filter': 'agTextColumnFilter', 'floatingFilter': True, 'filterParams': {'caseSensitive': False},                
                'minWidth': 70, 'maxWidth': 100},
            {'headerName': 'Tag', 'label': 'Tag', 'field': 'Tag', 'required': True, 'align': 'left', 'wrapHeaderText': True,
                'filter': 'agTextColumnFilter', 'floatingFilter': True, 'filterParams': {'caseSensitive': False},
                'minWidth': 70, 'maxWidth': 100},
            {'headerName': 'Duration', 'label': 'Duration', 'field': 'Duration', 'required': True, 'align': 'right', 'wrapHeaderText': True,
                'minWidth': 70, 'maxWidth': 100}
        ]


    def buildTableUserTags(data, title, tab, method):
        c= buildColumnsUserTag()
        if method=='create':
            with ui.row().classes('w-full h-full') as rowcontainer:
                CONTROLS[tab]['rowcontainer']=rowcontainer
                table = ui.aggrid({
                        'headerHeight': 40,
                        'defaultColDef': {'flex': 1}, 
                        'columnDefs': c,
                        'rowData': data,
                        }, auto_size_columns=True)
                table.style('width: calc(30%);height: calc(90%)')
                CONTROLS[tab]['download']=ui.button('Download', on_click=lambda: export_table_to_csv(tab))
                CONTROLS[tab]['columns']=c
                CONTROLS[tab]['rows']=data
        else :
            CONTROLS[tab]['rowcontainer'].parent_slot.parent.remove(CONTROLS[tab]['rowcontainer'])            
            with ui.row().classes('w-full h-full') as rowcontainer:
                CONTROLS[tab]['chart'].parent_slot.parent.remove(CONTROLS[tab]['chart'])
                CONTROLS[tab]['download'].parent_slot.parent.remove(CONTROLS[tab]['download'])            
                CONTROLS[tab]['rowcontainer']=rowcontainer
                table = ui.aggrid({
                        'headerHeight': 40,
                        'defaultColDef': {'flex': 1}, 
                        'columnDefs': c,
                        'rowData': data,
                        }, auto_size_columns=True)
                table.style('width: calc(30%);height: calc(90%)')
                CONTROLS[tab]['chart']=table
                CONTROLS[tab]['download']=ui.button('Download', on_click=lambda: export_table_to_csv(tab))
                CONTROLS[tab]['columns']=c
                CONTROLS[tab]['rows']=data
        return table

    def buildColumnsUserMonth():
        return [
            {'headerName': 'User', 'label': 'User', 'field': 'user', 'required': True, 'align': 'left', 
                'minWidth': 70, 'maxWidth': 100},
            {'headerName': 'Day', 'label': 'Day', 'field': 'day', 'required': True, 'align': 'left', 
                'minWidth': 70, 'maxWidth': 100},
            {'headerName': 'Task', 'label': 'Task', 'field': 'task', 'required': True, 'align': 'left', 'wrapHeaderText': True,
                'filter': 'agTextColumnFilter', 'floatingFilter': True, 'filterParams': {'caseSensitive': False},
                'minWidth': 40, 'maxWidth': 600},
            {'headerName': 'Tag', 'label': 'Tag', 'field': 'tag', 'required': True, 'align': 'left', 'wrapHeaderText': True,
                'filter': 'agTextColumnFilter', 'floatingFilter': True, 'filterParams': {'caseSensitive': False},
                'minWidth': 40, 'maxWidth': 100},
            {'headerName': 'Customer', 'label': 'Customer', 'field': 'customer', 'required': True, 'align': 'left', 'wrapHeaderText': True,
                'filter': 'agTextColumnFilter', 'floatingFilter': True, 'filterParams': {'caseSensitive': False},
                'minWidth': 40, 'maxWidth': 300},
            {'headerName': 'Duration', 'label': 'Duration', 'field': 'duration', 'required': True, 'align': 'right', 'wrapHeaderText': True,
                'minWidth': 40, 'maxWidth': 100}
        ]

    def buildTableUserMonth(data, title, tab, method):
        c= buildColumnsUserMonth()
        if method=='create':
            with ui.row().classes('w-full h-full') as rowcontainer:
                CONTROLS[tab]['rowcontainer']=rowcontainer
                table = ui.aggrid({
                        'headerHeight': 40,
                        'defaultColDef': {'flex': 1}, 
                        'columnDefs': c,
                        'rowData': data,
                        }, auto_size_columns=True)
                table.style('width: calc(60%);height: calc(90%)')
                CONTROLS[tab]['download']=ui.button('Download', on_click=lambda: export_table_to_csv(tab))
                CONTROLS[tab]['columns']=c
                CONTROLS[tab]['rows']=data
        else :
            CONTROLS[tab]['rowcontainer'].parent_slot.parent.remove(CONTROLS[tab]['rowcontainer'])            
            with ui.row().classes('w-full h-full') as rowcontainer:
                CONTROLS[tab]['chart'].parent_slot.parent.remove(CONTROLS[tab]['chart'])
                CONTROLS[tab]['download'].parent_slot.parent.remove(CONTROLS[tab]['download'])            
                CONTROLS[tab]['rowcontainer']=rowcontainer
                table = ui.aggrid({
                        'headerHeight': 40,
                        'defaultColDef': {'flex': 1}, 
                        'columnDefs': c,
                        'rowData': data,
                        }, auto_size_columns=True)
                table.style('width: calc(60%);height: calc(90%)')
                CONTROLS[tab]['chart']=table
                CONTROLS[tab]['download']=ui.button('Download', on_click=lambda: export_table_to_csv(tab))
                CONTROLS[tab]['columns']=c
                CONTROLS[tab]['rows']=data
        return table


    def buildToggles(mode,onlyYears=False, withTags=False):
        year, month=get_current_year_and_month()
        elements={}

        with ui.column():
            with ui.row():
                elements['year']=ui.toggle(YEARS, value=year)
                elements['switch'] = ui.switch('Months')
                elements['switch'].set_value(True)
            elements['month']=ui.toggle(MONTHS, value=get_month_name_from_value(month)).bind_visibility_from(elements['switch'], 'value')
        if onlyYears:
            elements['switch'].set_value(False)
            elements['switch'].set_visibility(False)
        if withTags:
            if mode == 'two':
                with ui.row():
                    elements['tags']=[]
                    for t in TAGS:
                        elements['tags'].append(ToggleButton(t))
            elif mode == 'three':   
                with ui.row():
                    elements['tags']=[]
                    for t in dbutils.taskDB.read_all_users():
                        elements['tags'].append(ToggleButton(t))
        return elements


    def refresh(mode):
        year=CONTROLS[mode]['toggles']['year'].value
        if CONTROLS[mode]['toggles']['switch'].value:
            month=MONTHS[CONTROLS[mode]['toggles']['month'].value]
        else:
            month=''
        (fromepoch, toepoch)=getEpochRange(year, month)
        if mode=='one':
            dbdata=dbutils.taskDB.read_summary_by_month_year(fromepoch, toepoch)
        elif mode=='two':
            # First collect the tags
            select=[]
            for i,t in enumerate(TAGS):
                if CONTROLS[mode]['toggles']['tags'][i]._state:
                    select.append(CONTROLS[mode]['toggles']['tags'][i].text)
            if len(select)==0:
                return
            else:
                dbdata=dbutils.taskDB.read_stats_by_user_activity(fromepoch, toepoch, select)
        elif mode=='three':
            # First collect the users
            select=[]
            for i,t in enumerate(dbutils.taskDB.read_all_users()):
                if CONTROLS[mode]['toggles']['tags'][i]._state:
                    select.append(CONTROLS[mode]['toggles']['tags'][i].text)
            if len(select)==0:
                return
            else:
                dbdata=dbutils.taskDB.read_stats_by_user_month(fromepoch, toepoch, select)
        else:
            return
        
        if mode in ['one']:
           # Process dbdata to build the UI data structure
            data=[{'value': el[1], 'name': el[0]} for el in dbdata]
        elif mode in ['two']:
           # Process dbdata to build the table structure
            data=[]
            for el in dbdata:
                newrow={}
                newrow['User']=el[0]
                newrow['Tag']=el[1]
                newrow['Duration']=secsToHHMM(el[2])
                data.append(newrow)
        elif mode in ['three']:
            # Process dbdata to build the task table
            data=[]
            for el in dbdata:
                newrow={}
                newrow['user']=el[0]
                (day,_)=fromEpochToDatetime(el[1])
                newrow['day']=day
                newrow['task']=el[2]
                newrow['tag']=el[3]
                newrow['customer']=el[4]
                newrow['duration']=secsToHHMM(el[5])
                data.append(newrow)


        if mode in ['one']:
            # remove previous chart if created
            if 'chart' in CONTROLS[mode]:
                buildPie(data, 'Hours by User', mode, 'update')
            else:
                # build new chart
                CONTROLS[mode]['chart']=buildPie(data, 'Hours by User', mode, 'create')
        elif mode in ['two']:  
            # remove previous chart if created
            if 'chart' in CONTROLS[mode]:
                buildTableUserTags(data, 'Hours by User/Activity', mode, 'update')
            else:
                # build new chart
                CONTROLS[mode]['chart']=buildTableUserTags(data, 'Hours by User/Activity', mode, 'create')  
        elif mode in ['three']:
            # remove previous chart if created
            if 'chart' in CONTROLS[mode]:
                buildTableUserMonth(data, 'Hours by User/Month', mode, 'update')
            else:
                # build new chart
                CONTROLS[mode]['chart']=buildTableUserMonth(data, 'Hours by User/Month', mode, 'create')
        else:
            return

        return

    if protectPage(app.storage.user.get('authenticated', False)):
        logNavigate('/login/')
        return
    
    header()
    setBackgroud()
    GEN_CLASSES=f'{COLORS['Ready']} w-full h-full'
    with ui.tabs().classes(GEN_CLASSES) as tabs:
        one = ui.tab('By Month/Year')
        two = ui.tab('By Month/Task')
        three = ui.tab('By User/Month')
    with ui.tab_panels(tabs, value=one).classes(GEN_CLASSES) as tab_panels:
        tab_panels.style('height: calc(100vh - 14rem)')
        with ui.tab_panel(one).classes(GEN_CLASSES):
            ui.label('Report by Month/Year')
            CONTROLS['one']={}
            CONTROLS['one']['toggles']=buildToggles('one')
            CONTROLS['one']['refresh']=ui.button('Refresh', on_click=lambda: refresh('one'))
        with ui.tab_panel(two).classes(GEN_CLASSES):
            ui.label('Report by Month/Task')
            CONTROLS['two']={}
            CONTROLS['two']['toggles']=buildToggles('two', withTags=True)
            CONTROLS['two']['refresh']=ui.button('Refresh', on_click=lambda: refresh('two'))
        with ui.tab_panel(three).classes(GEN_CLASSES):
            ui.label('Report by User/Month')
            CONTROLS['three']={}
            CONTROLS['three']['toggles']=buildToggles('three', withTags=True)
            CONTROLS['three']['refresh']=ui.button('Refresh', on_click=lambda: refresh('three'))
                
    footer()