from pywinauto_core import app_launch

ROBOT_LIBRARY_SCOPE = 'GLOBAL'


class _Listener:
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self):
        pass

    def start_suite(self, name, attrs):
        from pywinauto_core import on_enter_suite
        on_enter_suite()
        from logging import warning
        warning("START SUITE %s" % name)

    def start_test(self, name, attrs):
        from pywinauto_core import on_enter_test
        on_enter_test()

    def end_test(self, name, attrs):
        import logging
        from pywinauto_core import on_leave_test
        on_leave_test()

    def end_suite(self, name, attrs):
        from pywinauto_core import on_leave_suite
        on_leave_suite()
        from logging import warning
        warning("END SUITE %s" % name)

    def close(self):
        pass


ROBOT_LIBRARY_LISTENER = _Listener()

del _Listener