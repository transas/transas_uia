import logging
import re
from pywinauto.application import Application

from impl._params import Delay, fixed_val, pop, pop_re, pop_type, robot_args, pop_bool, pop_menu_path, str_2_bool
from impl._util import IronbotException, waiting_iterator, result_modifier, error_decorator, stop_monitoring, setup_monitoring


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
    (pop,), {
       'suite_teardown': (('teardown', fixed_val('suite')),),
       'test_teardown': (('teardown', fixed_val('test')),),
       'assert': (('_assert', fixed_val(True)),),
       'params': (('params', pop),),
       'workdir': (('workdir', pop),),
       'failure_text': (('failure_text', pop),),
    }
)


@robot_args(LAUNCH_PARAMS)
@error_decorator
def app_launch(executable, teardown=None, params='', _assert=False, **kw):
    """
    App Launch | <executable> [ | params | <cmdline parameters string> ] [ | flags and params ]

    Launches an app. The first parameter is a path to the app's executable. Optional 'suite_teardown' or 'test_teardown'
    flags force to kill the app at the end of the suite or of the test, respectively (if still running).
    A 'params' named parameter is also optional, should be followed by a parameters string (all args in one).

    :return: An application object or None in case of failure if "assert" flag is not present.

    """
    try:
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
    (pop,), {
       'suite_teardown': (('teardown', fixed_val('suite')),),
       'test_teardown': (('teardown', fixed_val('test')),),
       'failure_text': (('failure_text', pop),),
    }
)


@robot_args(APP_ATTACH_PARAMS)
@error_decorator
def app_attach(processes, teardown=None):
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
    apps = [Application().connect(process=p) for p in processes]
    if teardown == 'test':
        CONTROLLED_APPS[-1] += apps
    elif teardown == 'suite':
        CONTROLLED_APPS[-2] += apps
    if single:
        return apps[0]
    return apps


APP_STATE_PARAMS = (
    (pop,), {
       'running': (('running', fixed_val(True)),),
       'not_running': (('running', fixed_val(False)),),
       'kill': (('running', fixed_val(None)),),
       'timeout': (('timeout', pop_type(Delay)),),
       'assert': (('_assert', fixed_val(True)),),
       'any': (('any', fixed_val(True)),),
       'all': (('all', fixed_val(True)),),
       'single': (('single', fixed_val(True)),),
       'none': (('none', fixed_val(True)),),
       'number': (('number', pop_type(int)),),
       'failure_text': (('failure_text', pop),),
    }
)


@robot_args(APP_STATE_PARAMS)
@error_decorator
def app_state(app, running=True, timeout=Delay('0s'), any=False, all=False, single=False, none=False, _assert=False, number=None):
    """
    App State | <app> | params
    :param app: required, positional -- an application object;
    :param running: an optional flag -- the result is True if the app is running;
    :param not_running: an optional flag -- the result is True if the app is not running;
    :param kill: an optional flag -- same as not_running plus kills the app after waiting;
    :param assert: an optional flag -- fail keyword on failure;
    :param timeout: optional, followed by a delay value, e.g. *10s -- wait for the desired state.
    :return: True if the app state at the end of waiting is as desired, otherwise False
    """
    src_app = app
    if not isinstance(src_app, list):
        app = [app]

    kill = running is None
    running = bool(running)

    prefer_bool = all or any or single or none or not isinstance(src_app, list)

    for _ in waiting_iterator(timeout):
        res_list = []
        for a in app:
            res_list.append(bool(a.is_process_running()) == bool(running))
        ok, res, msg = result_modifier(res_list, src_list=src_app, any=any, all=all, single=single, none=none, number=number, prefer_bool=prefer_bool)
        if ok:
            break

    if kill:
        for a in app:
            if a.is_process_running():
                logging.warning('Killing an application')
                a.kill()
    if ok:
        return res
    if _assert:
        logging.error('App State failed: %s' % msg)
        raise PywinAutoCoreException('App State failed: %s' % msg)
    logging.warning('App State failed: %s' % msg)
    return res


def wnd_get(parent, wnd_name):
    if not isinstance(wnd_name, str):
        raise PywinAutoCoreException("Wnd Get: 'wnd_name' must be type str")
    return parent[wnd_name]


def cnt_get(window, cnt_title, cnt_type):
    if not isinstance(cnt_title, str):
        raise PywinAutoCoreException("Cnt Get: 'cnt_title' must be type str")
    if not isinstance(cnt_type, str):
        raise PywinAutoCoreException("Cnt Get: 'cnt_type' must be type str")
    return window.ChildWindow(title=cnt_title, control_type=cnt_type)
