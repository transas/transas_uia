import logging

from impl._params import parse, robot_args, parse_bool
from impl._util import Delay

from pywinauto import Desktop
from pywinauto.application import Application


class PywinAutoCoreException(Exception):
    pass


CONTROLLED_APPS = [] #None


def on_enter_test(app):
    CONTROLLED_APPS.append(app)

def on_enter_suite():
    CONTROLLED_APPS.append([])
    Delay.do_benchmarking()

def on_leave_test():
    for a in CONTROLLED_APPS[::-1]:
        if a.is_process_running():
            logging.warning('Test teardown: an app is still running')
            a.kill()
    del CONTROLLED_APPS[-1]

def on_leave_suite():
    for a in CONTROLLED_APPS[-1]:
        if a.is_process_running():
            logging.warning('Suite teardown: an app is still running')
            a.kill()
    del CONTROLLED_APPS[-1]

LAUNCH_PARAMS = (
    (parse,),
    {
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
    (parse,),
    {
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

def get_window(app, window_name, use_desktop=False, backend=None):
    if use_desktop:
        return Desktop(backend=backend)[window_name]
    else:
        return app[window_name]

def get_parent_element(parent, element_name=None, **kwargs):
    if element_name is None:
        return parent.child_window(**kwargs)
    else:
        return parent[element_name]

def element_wait(element, wait_for, timeout=None, retry_interval=None):
    """
    pywinauto doc:
    :param wait_for: The state to wait for the window to be in. It can
        be any of the following states, also you may combine the states by space key.
         * 'exists' means that the window is a valid handle
         * 'visible' means that the window is not hidden
         * 'enabled' means that the window is not disabled
         * 'ready' means that the window is visible and enabled
         * 'active' means that the window is active
    """
    return element.wait(wait_for, timeout, retry_interval)

def do_action(parent, action, **kwargs):
    act = getattr(parent, action)
    if callable(act):
        act(**kwargs)
    else:
        raise PywinAutoCoreException()

CLICK_BUTTON_PARAMS = (
    (parse,),
    {
       'title': ('title', parse),
       'title_re': ('title_re', parse),
       'control_id': ('control_id', parse),
       'auto_id': ('auto_id', parse),
    }
)

@robot_args(CLICK_BUTTON_PARAMS)
def click_button(window, control_type="Button", **kwargs):
    window.child_window(control_type=control_type, **kwargs).click()


if __name__ == "__main__":

    app = app_launch('notepad.exe', backend='uia')
    on_enter_test(app)
    win = get_window(app, 'Untitled - Notepad')
    on_leave_test()
