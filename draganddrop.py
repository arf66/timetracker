from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Protocol

from nicegui import app,ui
from constants import COLORS, TAGS_COLORS, TAGS_TEXT_COLORS
from tasks import moveTask, removeTask, duplicateTask
from utility import logNavigate, sync_db, secsToHHMM, daysDifference
from containers import UIContainers


class Item(Protocol):
    id: str
    title: str
    tag: str
    customer: str
    duration: int
    due: str


@dataclass
class ToDo:
    id: str
    title: str
    tag: str
    status: str
    customer: str
    duration: int
    due: str


dragged: Optional[card] = None
containers=UIContainers()


class column(ui.scroll_area):

    def __init__(self, name: str, on_drop: Optional[Callable[[Item, str], None]] = None) -> None:
        super().__init__()
        with self.classes(f'{COLORS[name]} w-96 p-4 rounded shadow-2'):
            self.style('height: calc(100vh - 12rem)')
            ui.label(name).classes('text-bold text-2xl text-blue-500 font-[Roboto]')
        self.name = name
        self.on('dragover.prevent', self.highlight)
        self.on('dragleave', self.unhighlight)
        self.on('drop', self.move_card)
        self.on_drop = on_drop

    def highlight(self) -> None:
        std_col=COLORS[self.name]
        hi_col='bg-blue-grey-3'
        self.classes(remove=std_col, add=hi_col)

    def unhighlight(self) -> None:
        std_col=COLORS[self.name]
        hi_col='bg-blue-grey-3'
        self.classes(remove=hi_col, add=std_col)

    def move_card(self) -> None:
        global dragged  # pylint: disable=global-statement # noqa: PLW0603
        self.unhighlight()
        if dragged.parent_slot.parent.name == 'Done':
            return
        dragged.parent_slot.parent.remove(dragged)
        with self:
            card(dragged.item)
            moveTask(app.storage.user["username"], dragged.item.id, self.name)
        self.on_drop(dragged.item, self.name)
        dragged = None


class card(ui.card):

    def delCard(self, id):
        self.parent_slot.parent.remove(self)
        removeTask(app.storage.user["username"], id)

    def goToDetails(self, id):
        sync_db()
        logNavigate(f'/details/?id={id}')

    def copyCard(self, id):
        dup=duplicateTask(app.storage.user["username"], id)
        with containers.get('Ready'):
            due= str(daysDifference(dup['due_time']))
            el = card(ToDo(dup['id'], dup['title'], dup['tag'], 'Ready', dup['customer'], dup['duration'], due))
        

    def __init__(self, item: Item) -> None:
        super().__init__()
        self.item = item
        with self.props('draggable').classes('w-full cursor-pointer bg-grey-1').style('gap: 0.1rem'):
            with ui.row().classes('w-full items-baseline').style('gap: 0.1rem'):
                ui.label(item.title).classes('w-2/3 font-[Roboto] font-light')
                ui.space()
                if self.parent_slot.parent.name != 'Done':
                    itemcolor='red' if int(item.due) < 0 else 'gray'
                    item.due=item.due[1:] if item.due[0]=='-' else item.due
                    ui.chip(item.due, color=itemcolor, removable=False).set_enabled(False)
                    ui.space()
                if item.duration>0:
                    with ui.icon('schedule', color='lime-400').classes('text-xl'):
                        ui.tooltip(f'Already consumed: {secsToHHMM(item.duration)}')    
            with ui.row().classes('w-full items-baseline').style('gap: 0.1rem'):
                ui.chip(item.tag, color=TAGS_COLORS[item.tag], text_color=TAGS_TEXT_COLORS[item.tag]).classes('text-xs')
                ui.label(item.customer).classes('text-xs text-blue-600/75')
                ui.space()
                if self.parent_slot.parent.name != 'Done':
                    with ui.button(icon='delete', on_click=lambda: self.delCard(item.id)).props('flat').classes('text-xs'):
                        ui.tooltip('Delete task')                
                if self.parent_slot.parent.name == 'Done':
                    with ui.button(icon='content_copy', on_click=lambda: self.copyCard(item.id)).props('flat').classes('text-xs'):
                        ui.tooltip('Duplicate task')
                with ui.button(icon='open_in_new', on_click=lambda: self.goToDetails(item.id)).props('flat').classes('text-xs'):
                    ui.tooltip('View full task details')
        self.on('dragstart', self.handle_dragstart)

    def handle_dragstart(self) -> None:
        global dragged  # pylint: disable=global-statement # noqa: PLW0603
        dragged = self
