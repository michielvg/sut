import builtins
import select
import sys
import warnings

from enum import Enum

class Style(Enum):
    RED = "\033[91m"
    YELLOW = "\033[93m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"

class TUI:
    def __init__(self, prompt: str = "SUT> "):
        self.prompt = prompt
        self.enable()
    
    def enable(self):
        if hasattr(builtins, "tui") and builtins.tui is not self:
            warnings.warn("Overwriting builtin 'tui'")
            builtins.tui = self

        if getattr(builtins, "print") is not self.print:
            self._print_ = builtins.print
            builtins.print = self.print

    def disable(self):
        builtins.print = self._print_

    def _print_prompt(self):
        sys.stdout.write(self.prompt)
        sys.stdout.flush()

    def print(self, msg: str, *styles: Style):
        """
        Print a message with optional ANSI styles.
        If no styles are provided, defaults to RESET (normal text).
        """
        sys.stdout.write("\r\033[K")  # clear line

        if not styles:
            styles = (Style.RESET,)

        style_codes = "".join(s.value for s in styles)
        sys.stdout.write(f"{style_codes}{msg}{Style.RESET.value}\n")
        self._print_prompt()
        sys.stdout.flush()

    def input_poll(self) -> str | None:
        rlist, _, _ = select.select([sys.stdin], [], [], 0)
        if sys.stdin in rlist:
            return sys.stdin.readline().rstrip("\n")
        return None

    def input_bool(self, prompt: str, default: bool = True) -> bool:
        yes_no = "Y/n" if default else "y/N"
        while True:
            ans = input(f"{prompt} ({yes_no}): ").strip().lower()
            if not ans:
                return default
            if ans in ("y", "yes"):
                return True
            if ans in ("n", "no"):
                return False