import traceback
import multiprocessing
import threading
import sys
from typing import Optional

def format_stack_trace(exctype, value, tb, nested: bool = False,stackTraceMode: bool = False) -> str:
    tb_list = traceback.extract_tb(tb)

    if nested:
        exception_info = f"{exctype.__name__}: {value}\n"
    else:
        if not stackTraceMode:
            exception_info = f"Exception in process: {multiprocessing.current_process().name}, thread: {threading.current_thread().name}; {exctype.__name__}: {value}\n"
            exception_info += "Traceback (most recent call last):\n"
        else:
            exception_info = "This is just a stack trace\n"
            exception_info += "Traceback (most recent call last):\n"

    for filename, lineno, funcname, line in tb_list:
        exception_info += f"  at {funcname} in ({filename}:{lineno})\n"
    
    # 检查是否有原因和其他信息
    cause = getattr(value, '__cause__', None)
    context = getattr(value, '__context__', None)
    
    if cause:
        exception_info += "Caused by: "
        exception_info += format_stack_trace(type(cause), cause, cause.__traceback__, nested=True)
    if context and not cause:
        exception_info += "original exception: "
        exception_info += format_stack_trace(type(context), context, context.__traceback__, nested=True)
    
    return exception_info

def ExtractException(exctype, e, tb) -> Optional[str]:
    # 获取回溯信息并格式化为字符串
    tb_str = format_stack_trace(exctype, e, tb)
    
    # 记录异常信息到日志
    exception_info = ""
    exception_info += tb_str
    # 返回异常信息
    return exception_info

def GetStackTrace(vokedepth: int = 1) -> str:
    """
    获取堆栈跟踪信息
    """
    # 获取当前调用栈信息的前两层
    stack = traceback.extract_stack(limit=vokedepth)
    stack_info = "Stack Trace:\n"
    for frame in stack[:-vokedepth+1]:
        filename = frame.filename
        line = frame.lineno
        funcname = frame.name
        stack_info += f"  at {funcname} in ({filename}:{line})\n"
    return stack_info

def exechook(type, value, tb):
    """
    异常处理钩子函数
    """
    err_stack = ExtractException(type, value, tb)
    sys.stderr.write(err_stack)
    sys.stderr.flush()

sys.excepthook = exechook