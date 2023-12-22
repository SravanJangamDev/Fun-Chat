from traceback import format_exception
from sys import stderr, _getframe
from datetime import datetime
import json
import os
from typing import Optional
from uuid import uuid4
from config import PUBSUB_DEBUG_MODE, PUBSUB_ERROR_LOG

# *************************************************************************** #
#                                 Log Functions                               #
# *************************************************************************** #


def write_log(
    svrty: str,
    err_msg: str = "",
    excp: Optional[Exception] = None,
    notify: bool = False,
) -> None:
    tracker_id = str(uuid4())
    log_details: dict = {
        "svrty": svrty.upper(),
        "family": "pubsub",
        "tracker_id": tracker_id,
        "time_stamp": str(datetime.now()),
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

        if PUBSUB_ERROR_LOG:
            with open(PUBSUB_ERROR_LOG, "a") as f:
                f.write(f"{json.dumps(log_details)}\n")

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
    if PUBSUB_DEBUG_MODE:
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

        if PUBSUB_DEBUG_MODE:
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


class FatalException(Exception):
    def __init__(
        self,
        err_msg: str = "",
        excp: Optional[Exception] = None,
    ):
        self.excp = excp
        self.err_msg = err_msg
        write_log("crach", err_msg, excp, notify=True)

    def __str__(self) -> str:
        if self.excp:
            return f"{type(self.excp).__name__} {self.err_msg}"
        else:
            return self.err_msg


# /******************************************************************/


def create_unique_id() -> str:
    return str(uuid4())


def read_file(filepath: str, list: bool = False):
    data = {}
    try:
        with open(filepath, "r") as f:
            data = json.load(f)

    except Exception as e:
        raise TempException(f"Unable to read the file. {filepath}", excp=e)

    return data


def read_file_list(filepath: str):
    data = []
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
            data = [json.loads(line) for line in lines]

    except Exception as e:
        raise TempException(f"Unable to read the file. {filepath}", excp=e)

    return data


def create_file(filepath: str, data: dict) -> None:
    try:
        with open(filepath, "w") as f:
            json.dump(data, f)

    except Exception as e:
        raise TempException(f"Unable to create the file. {filepath}", excp=e)


def update_file(filepath: str, data: dict) -> None:
    try:
        old_data = {}
        if is_file_exists(filepath):
            old_data = read_file(filepath)

        data = {**old_data, **data}
        with open(filepath, "w") as f:
            json.dump(data, f)

    except Exception as e:
        raise TempException(f"Unable to create the file. {filepath}", excp=e)


def append_to_file(filepath: str, data: dict) -> None:
    try:
        with open(filepath, "a") as f:
            f.write(f"{json.dumps(data)}\n")

    except Exception as e:
        raise TempException(f"Unable to update the file. {filepath}", excp=e)


def remove_file(filepath: str) -> None:
    if is_file_exists(filepath):
        os.remove(filepath)


def is_file_exists(filepath: str) -> bool:
    return os.path.exists(filepath)


def create_folder(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


def get_subfolders(path: str) -> list:
    files = []
    try:
        files = os.listdir(path)
        files = [f for f in files if os.path.isdir(f"{path}/{f}")]
    except Exception as e:
        log_crash(f"Unable to read the folder. {path}", excp=e)

    return files


def get_subfiles(path: str) -> list:
    files = []
    try:
        files = os.listdir(path)
        files = [f for f in files if os.path.isfile(f"{path}/{f}")]
    except Exception as e:
        log_issue(f"Unable to read the folder. {path}", excp=e)

    return files
