import logging
import re
from pywinauto.application import Application

from impl._params import fixed_val, parse, parse_re, robot_args, parse_bool, pop_menu_path, str_2_bool
from impl._util import Delay, IronbotException, waiting_iterator, result_modifier, stop_monitoring, setup_monitoring


class PywinAutoCoreException(Exception):
    pass


CONTROLLED_APPS = [] #None


def on_enter_test():
    CONTROLLED_APPS.append([])


def on_enter_suite():
    CONTROLLED_APPS.append([])
    Delay.do_benchmarking()


def on_leave_test():
    for a in CONTROLLED_APPS[-1]:
        if a.is_process_running():
            logging.warning('Test teardown: an app is still running')
            a.kill()
    del CONTROLLED_APPS[-1]
    stop_monitoring()


def on_leave_suite():
    for a in CONTROLLED_APPS[-1]:
        if a.is_process_running():
            logging.warning('Suite teardown: an app is still running')
            a.kill()
    del CONTROLLED_APPS[-1]


LAUNCH_PARAMS = (
    (parse,), {
       'teardown': ('teardown', parse),
       'assert': ('_assert', parse_bool),
       'params': ('params', parse),
       'workdir': ('workdir', parse),
       'failure_text': ('failure_text', parse),
       'backend': ('backend', parse),
    }
)


@robot_args(LAUNCH_PARAMS)
def app_launch(executable, backend=None, teardown=None, params='', _assert=False, **kw):
    """
    App Launch | <executable> [ | params | <cmdline parameters string> ] [ | flags and params ]

    Launches an app. The first parameter is a path to the app's executable. Optional 'suite_teardown' or 'test_teardown'
    flags force to kill the app at the end of the suite or of the test, respectively (if still running).
    A 'params' named parameter is also optional, should be followed by a parameters string (all args in one).

    :return: An application object or None in case of failure if "assert" flag is not present.

    """
    try:
        if backend is not None:
            app = Application(backend=backend).start(executable)
        else:
            app = Application().start(executable)
    except:
        if _assert:
            logging.error('Failed to launch an executable')
            raise
        logging.warning('Failed to launch an executable')
        return None
    if teardown == 'test':
        CONTROLLED_APPS[-1].append(app)
    elif teardown == 'suite':
        CONTROLLED_APPS[-2].append(app)

    return app


APP_ATTACH_PARAMS = (
    (parse,), {
       'teardown': ('teardown', parse),
       'failure_text': ('failure_text', parse),
       'backend': ('backend', parse),
    }
)


@robot_args(APP_ATTACH_PARAMS)
def app_attach(processes, backend=None, teardown=None):
    """
    App Attach | <proc_or_proc_list> [ | test_teardown/suite_teardown ]

    Creates application objects for a process or for a list of processes. If test_teardown or
    suite_teardown is present, the applications are going to be terminated when the test (or
    the suite) finishes.

    :return: List of applications (if a list of processes is given) or an
        application (in case of a single process that is not wrapped into a list object).
        Note: a list containing a single process is still a list.
    """
    single = not isinstance(processes, list)
    if single:
        processes = [processes]
    if backend is not None:
        apps = [Application(backend=backend).connect(process=p) for p in processes]
    else:
        apps = [Application().connect(process=p) for p in processes]
    if teardown == 'test':
        CONTROLLED_APPS[-1] += apps
    elif teardown == 'suite':
        CONTROLLED_APPS[-2] += apps
    if single:
        return apps[0]
    return apps


def wnd_get(parent, wnd_name):
    return parent[wnd_name]


CLICK_BUTTON_PARAMS = (
    (parse,), {
       'title': ('title', parse),
       'title_re': ('title_re', parse),
       'control_id': ('control_id', parse),
       'auto_id': ('auto_id', parse),
    }
)


@robot_args(CLICK_BUTTON_PARAMS)
def click_button(window, title=None, title_re=None, control_id=None, auto_id=None):
    if title is not None:
        window.window(title=title, control_type="Button").click()
    elif title_re is not None:
        window.window(title_re=title_re, control_type="Button").click()
    elif control_id is not None:
        window.window(control_id=control_id, control_type="Button").click()
    elif auto_id is not None:
        window.window(auto_id=auto_id, control_type="Button").click()


if __name__ == "__main__":
    on_enter_suite()
    on_enter_test()
    app = app_launch("calc.exe", backend="uia", teardown="test")
    w = wnd_get(app, "Calculator")
    click_button(w, title_re="4+")
    on_leave_test()
    on_leave_suite()