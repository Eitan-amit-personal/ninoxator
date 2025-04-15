import os


def verbose_mode() -> bool:
    return os.getenv("NINOXATOR_DEBUG", "true").lower() == "true"


def set_verbose_mode(verbose: bool):
    os.environ["NINOXATOR_DEBUG"] = "true" if verbose else "false"


def toggle_verbose_mode():
    set_verbose_mode(not verbose_mode())
