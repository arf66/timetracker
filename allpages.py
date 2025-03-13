from nicegui import ui
from kanban import kanban_page
from loginpage import login_page
from logoutpage import page_logout
from signuppage import signup_page
from taskdetails import details_page

def create():
    ui.page('/kanban/')(kanban_page)
    ui.page('/login/')(login_page)
    ui.page('/logout/')(page_logout)
    ui.page('/signup/')(signup_page)
    ui.page('/details/')(details_page)
