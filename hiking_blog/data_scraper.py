from threading import Thread


def async_update_gear_info(function):
    thread = Thread(target=function)
    thread.daemon = True
    thread.start()
