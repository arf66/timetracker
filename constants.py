UI_STATUSES=['Ready', 'Doing', 'Done']
DB_STATUSES=['Ready', 'Doing', 'Done', 'Deleted', 'Archived']
YEARS=['2024', '2025']
MONTHS={'Jan':'01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 
        'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
COLORS={'Ready': 'bg-gray-200 opacity-85', 
        'Doing': 'bg-lime-200 opacity-85', 
        'Done': 'bg-red-300 opacity-85'}
TAGS=['ADM', 'ENG', 'DEV', 'QAT', 'OPS', 'PRE', 'SAL', 'TRA', 'REG']
TAGS_COLORS={'ADM':'grey-100', 
             'ENG':'sky-100', 
             'DEV':'sky-100', 
             'QAT':'sky-100', 
             'OPS':'red-100', 
             'PRE':'green-100',
             'MKT': 'orange-100', 
             'SAL': 'purple-100', 
             'TRA':'yellow-100',
             'REG': 'orange-100'}
TAGS_TEXT_COLORS={
             'ADM':'black-600', 
             'ENG':'black-600', 
             'DEV':'black-600', 
             'QAT':'black-600', 
             'OPS':'black-600', 
             'PRE':'black-600', 
             'MKT':'black-600', 
             'SAL':'black-600', 
             'TRA':'black-600',
             'REG': 'black-600'}
ROLES=['User', 'Admin']
DEFAULT_ROLE='User'
ADMIN_ROLE='Admin'
DATABASE='timetracker.db'
DEFAULT_TZ='CET'
DEBUG=False
VERSION='0.19'