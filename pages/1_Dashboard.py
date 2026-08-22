from utils.page import init_page
from components.welcome_banner import welcome_banner
from components.dashboard_cards import dashboard_cards
from components.charts import damage_chart
from components.system_status import system_status
from components.recent_activity import recent_activity
from components.quick_actions import quick_actions

init_page("Dashboard", "📊")

welcome_banner()

dashboard_cards()

damage_chart()

system_status()

recent_activity()

quick_actions()