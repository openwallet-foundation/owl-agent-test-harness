import functools
import json
import os
import uuid

from timeit import default_timer

import asyncio
import prompt_toolkit
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

import pygments
from pygments.filter import Filter
from pygments.lexer import Lexer
from pygments.lexers.data import JsonLdLexer
from prompt_toolkit.formatted_text import FormattedText, PygmentsTokens

COLORIZE = bool(os.getenv("COLORIZE", True))
MAIN_LOOP = asyncio.get_event_loop()
session = PromptSession()

class PrefixFilter(Filter):
    def __init__(self, **options):
        Filter.__init__(self, **options)
        self.prefix = options.get("prefix")

    def lines(self, stream):
        line = []
        for ttype, value in stream:
            if "\n" in value:
                parts = value.split("\n")
                value = parts.pop()
                for part in parts:
                    line.append((ttype, part))
                    line.append((ttype, "\n"))
                    yield line
                    line = []
            line.append((ttype, value))
        if line:
            yield line

    def filter(self, lexer, stream):
        if isinstance(self.prefix, str):
            prefix = ((pygments.token.Generic, self.prefix),)
        elif self.prefix:
            prefix = self.prefix
        else:
            prefix = ()
        for line in self.lines(stream):
            yield from prefix
            yield from line


def print_lexer(
    body: str, lexer: Lexer, label: str = None, prefix: str = None, indent: int = None
):
    if COLORIZE:
        prefix_str = prefix + " " if prefix else ""
        if prefix_str or indent:
            prefix_body = prefix_str + " " * (indent or 0)
            lexer.add_filter(PrefixFilter(prefix=prefix_body))
        tokens = list(pygments.lex(body, lexer=lexer))
        if label:
            fmt_label = [("fg:ansimagenta", label)]
            if prefix_str:
                fmt_label.insert(0, ("", prefix_str))
            print_formatted(FormattedText(fmt_label))
        print_formatted(PygmentsTokens(tokens))
    else:
        print_ext(body, label=label, prefix=prefix)


def print_json(data, label: str = None, prefix: str = None, indent: int = 2):
    if isinstance(data, str):
        data = json.loads(data)
    data = json.dumps(data, indent=2)
    prefix_str = prefix or ""
    print_lexer(data, JsonLdLexer(), label=label, prefix=prefix_str, indent=indent)


def print_formatted(*args, **kwargs):
    prompt_toolkit.print_formatted_text(*args, **kwargs)


def print_ext(
    *msg,
    color: str = None,
    label: str = None,
    prefix: str = None,
    indent: int = None,
    **kwargs,
):
    prefix_str = prefix or ""
    if indent:
        prefix_str += " " * indent
    if color and COLORIZE:
        msg = [(color, " ".join(map(str, msg)))]
        if prefix_str:
            msg.insert(0, ("", prefix_str + " "))
        if label:
            msg.insert(0, ("fg:ansimagenta", label + "\n"))
        print_formatted(FormattedText(msg), **kwargs)
        return
    if label:
        print(label, **kwargs)
    if prefix_str:
        msg = (prefix_str, *msg)
    print(*msg, **kwargs)

def _run_in_main(func):
    MAIN_LOOP.call_soon_threadsafe(run_in_terminal, func)

def output_reader(handle, callback, *args, **kwargs):
    if handle is None:
        return

    for line in iter(handle.readline, b""):
        if not line and line != "":
            break
        _run_in_main(functools.partial(callback, line, *args))


def log_msg(*msg, color="fg:ansimagenta", **kwargs):
    _run_in_main(lambda: print_ext(*msg, color=color, **kwargs))


def log_json(data, **kwargs):
    _run_in_main(lambda: print_json(data, **kwargs))


def log_status(status: str, **kwargs):
    log_msg(f"\n{status}", color="bold", **kwargs)


def flatten(args):
    for arg in args:
        if isinstance(arg, (list, tuple)):
            yield from flatten(arg)
        else:
            yield arg


def prompt_init():
    if hasattr(prompt_init, "_called"):
        return
    prompt_init._called = True
    use_asyncio_event_loop()


async def prompt(*args, **kwargs):
    prompt_init()
    with patch_stdout():
        try:
            while True:
                tmp = await PromptSession().prompt_async(*args, **kwargs)
                if tmp:
                    break
            return tmp
        except EOFError:
            return None


async def prompt_loop(*args, **kwargs):
    while True:
        option = await prompt(*args, **kwargs)
        yield option


class DurationTimer:
    def __init__(self, label: str = None, callback=None):
        self.callback = callback
        self.duration = None
        self.label = label
        self.last_error = None
        self.total = 0.0
        self.init_time = self.now()
        self.start_time = None
        self.stop_time = None
        self.running = False

    @classmethod
    def now(cls):
        return default_timer()

    def start(self):
        self.start_time = self.now()
        self.running = True

    def stop(self):
        if not self.running:
            return
        self.stop_time = self.now()
        self.duration = self.stop_time - self.start_time
        self.running = False
        self.total += self.duration
        if self.callback:
            self.callback(self)

    def cancel(self):
        self.running = False

    def reset(self):
        self.duration = None
        self.total = 0.0
        self.last_error = None
        restart = False
        if self.running:
            self.stop()
            restart = True
        self.start_time = None
        self.stop_time = None
        if restart:
            self.start()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, err_type, err_value, err_tb):
        self.last_error = err_value
        self.stop()


def log_timer(label: str, show: bool = True, logger=None, **kwargs):
    logger = logger or log_msg
    cb = (
        (
            lambda timer: timer.last_error
            or logger(timer.label, f"{timer.duration:.2f}s", **kwargs)
        )
        if show
        else None
    )
    return DurationTimer(label, cb)


def create_uuid():
    return str(uuid.uuid4())


def pad_base64(value: str) -> str:
    if len(value) % 4 != 0:
        n_missing = 4 - (len(value) % 4)
        value = value + (n_missing * "=")
    return value
