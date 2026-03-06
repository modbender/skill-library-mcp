class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    @staticmethod
    def colorize(text, color):
        return f"{color}{text}{Color.END}"

def print_header(text):
    print(f"\n{Color.BOLD}{Color.CYAN}{text}{Color.END}")

def print_success(text):
    print(f"{Color.GREEN}{text}{Color.END}")

def print_error(text):
    print(f"{Color.RED}{text}{Color.END}")

def print_warning(text):
    print(f"{Color.YELLOW}{text}{Color.END}")

def print_key_value(key, value):
    print(f"{Color.BOLD}{key}:{Color.END} {value}")
