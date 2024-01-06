from traceback import format_exception
from sys import stderr, _getframe
from datetime import datetime
import json
from typing import Optional
from uuid import uuid4
from config import ERROR_LOG, DEBUG_MODE

# *************************************************************************** #
#                                 Log Functions                               #
# *************************************************************************** #


def write_log(
    svrty: str,
    err_msg: str = "",
    excp: Optional[Exception] = None,
    notify: bool = False,
) -> None:
    print("Message", err_msg, excp)
    tracker_id = str(uuid4())
    log_details: dict = {
        "svrty": svrty.upper(),
        "family": "pubsub",
        "tracker_id": tracker_id,
        "time_stamp": datetime.now().strftime("%Y-%m-%d %H:%M%S"),
        "err_msg": err_msg,
    }

    excp_msg = None
    filename = None
    lineno = None
    try:
        if excp:
            excp_msg = "".join(
                format_exception(excp.__class__, excp, excp.__traceback__)
            )

        frameinfo = _getframe().f_back
        if frameinfo:
            filename = frameinfo.f_code.co_filename
            lineno = frameinfo.f_lineno
            frameinfo = frameinfo.f_back
            if frameinfo:
                filename = frameinfo.f_code.co_filename
                lineno = frameinfo.f_lineno

        log_details["filename"] = filename
        log_details["lineno"] = lineno
        log_details["Exception"] = excp_msg

        if ERROR_LOG:
            with open(ERROR_LOG, "a") as f:
                f.write(f"{json.dumps(log_details, indent=2)}\n")

        else:
            stderr.write(json.dumps(log_details))

    except Exception:
        stderr.write(json.dumps(log_details))

    if notify:
        notify_msg = ""
        for key, val in log_details.items():
            notify_msg += f"{key.upper()}: {val}\n"

        # notify_on_slack(notify_msg)


def log_info(err_msg: str, notify: bool = False) -> None:
    if DEBUG_MODE:
        write_log("info", err_msg, notify=notify)


def log_issue(
    err_msg: str, excp: Optional[Exception] = None, notify: bool = False
) -> None:
    write_log("issue", err_msg, excp=excp, notify=notify)


def log_crash(
    err_msg: str, excp: Optional[Exception] = None, notify: bool = False
) -> None:
    write_log("crash", err_msg, excp=excp, notify=notify)


# *************************************************************************** #
#                             Exception Class                                 #
# *************************************************************************** #


class ClientException(Exception):
    def __init__(
        self,
        err_msg: str = "Bad Request",
        excp: Optional[Exception] = None,
    ):
        self.excp = excp
        self.err_msg = err_msg

        if DEBUG_MODE:
            write_log("info", err_msg, excp)

    def __str__(self) -> str:
        if self.excp:
            return f"{self.excp.__class__.__name__} {self.err_msg}"
        else:
            return self.err_msg


class TempException(Exception):
    def __init__(
        self,
        err_msg: str = "",
        excp: Optional[Exception] = None,
    ):
        self.excp = excp
        self.err_msg = err_msg
        write_log("issue", err_msg, excp, notify=True)

    def __str__(self) -> str:
        if self.excp:
            return f"{type(self.excp).__name__} {self.err_msg}"
        else:
            return self.err_msg
