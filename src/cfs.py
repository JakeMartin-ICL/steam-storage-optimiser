import sys
from colorama import init, Fore, Style
init()


def colour_first_sentence(message, colour):
    sentences = message.split('.', maxsplit=1)
    if len(sentences) == 1:
        return f"{colour}{sentences[0]}{Style.RESET_ALL}"
    return f"{colour}{sentences[0]}.{Style.RESET_ALL} {sentences[1]}"


def ok(message):
    print(colour_first_sentence(message, Fore.GREEN + Style.BRIGHT))


def warn(message):
    print(colour_first_sentence(message, Fore.YELLOW + Style.BRIGHT))


def note(message):
    print(colour_first_sentence(message, Fore.CYAN + Style.BRIGHT))


def error(message):
    print(colour_first_sentence(message, Fore.RED + Style.BRIGHT))
    input("Press Enter to quit . . .")
    sys.exit(1)
