'''
Module:
  Sample code of using compliant_handle(file=sys.stderr) in matrixlib.scrubber

Description:

Without calling compliant_handle(), the exception will be shown as below
    Traceback (most recent call last):
    File "sample.py", line 29, in <module>
        1 / 0
    ZeroDivisionError: division by zero

Sample code's stderr output:

--------------------------------------------------
compliant_handle() scrub exception message, print traceback and exception type to StdErr of AEther client, and raise exception:
SystemLog: Traceback (most recent call last):
SystemLog:   File "sample.py", line 29, in <module>
SystemLog:     1 / 0
SystemLog: ZeroDivisionError: **Exception Message Scrubbed**
--------------------------------------------------
'''

import sys
import datetime
import functools
from traceback import TracebackException


def scrub_exc_message(tb_exc):
    # type: (traceback.TracebackException) -> traceback.TracebackException
    '''Scrub messages from a TracebackException object
    :param traceback.TracebackException tb_exc: The original TracebackException object
    :rtype traceback.TracebackException
    :return: a TracebackException object with scrubbed messages
    :notes: only scrub execption message for Non-SyntaxError exception
    '''
    tb_exc._str = '**Exception Message Scrubbed**'  # pylint: disable=W0212
    if tb_exc.__cause__:
        tb_exc.__cause__ = scrub_exc_message(tb_exc.__cause__)
    if tb_exc.__context__:
        tb_exc.__context__ = scrub_exc_message(tb_exc.__context__)
    return tb_exc


def mprint_exc(scrub_exc_msg=True, file=sys.stderr):
    '''Print exception to StdErr of AEther client.
    By defaut, it scrub exception message, print traceback and exception type.
    :param bool scrub_exc_msg: wheather scrub exception message.
    '''
    tb_exc = TracebackException(*sys.exc_info())
    if scrub_exc_msg:
        tb_exc = scrub_exc_message(tb_exc)
    exc_list = list(tb_exc.format())
    for exc in exc_list:
        if "return function(*matrix_args, **matrix_kwargs)" in exc:
            # dow not show Traceback for compliant_handle
            continue
        lines = exc.splitlines()
        for line in lines:
            timestamp = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            print("SystemLog: [%s] %s" % (timestamp, line), file=file)


def compliant_handle(file=sys.stderr):
    '''
    A decorator that wraps the passed in function and prints
    exceptions should one occur in a compliant way.
    Prints only the name and the traceback.

    Usage: Just add @compliant_handle on top of your function definition.
    Example:
        Before:
        def foo(x):
            pass

        After:
        @compliant_handle()
        def foo(x):
            pass

    :param file: Optional stream to write to, by default it is stderr
    '''
    def decorator(function):
        '''
        create a decroator to catch exception and log
        https://www.blog.pythonlibrary.org/2016/06/09/python-how-to-create-an-exception-logging-decorator/
        '''
        @functools.wraps(function)
        def wrapper(*matrix_args, **matrix_kwargs):
            '''
            create a wrapper to catch exception and log
            '''
            try:
                return function(*matrix_args, **matrix_kwargs)
            except BaseException:
                mprint_exc(True, file)
                # re-raise the exception
                raise
        return wrapper
    return decorator
