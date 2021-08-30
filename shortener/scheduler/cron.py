from shortener.urls.telegram_handler import command_handler
from shortener.ga import visitors


def visitor_collector():
    visitors()

def telegram_command_handler():
    command_handler()