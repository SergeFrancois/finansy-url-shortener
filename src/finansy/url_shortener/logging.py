import inspect
import logging


def make_log_record(*args, **kw):
    try:
        stack = inspect.stack()
        class_name = None
        i = 4
        while True:
            caller = stack[i][0].f_locals.get('self')
            if caller:
                if isinstance(caller, logging.Logger):
                    i += 1
                    continue
                else:
                    class_name = caller.__class__.__qualname__
                    break
            break
        record = logging.LogRecord(*args, **kw)
        record.fullModuleName = record.module
        module = inspect.getmodule(stack[i][0])
        if module and module.__package__:
            record.fullModuleName = f'{module.__package__}.{record.module}'
        record.className = class_name
        if record.className:
            record.funcName = f'{record.className}.{record.funcName}'
        return record
    finally:
        del stack
