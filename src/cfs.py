import os
import sys
from colorama import init, Fore, Back, Style
init()


def colour_first_sentence(message, colour):
    sentences = message.split('.', 1)
    return f"{colour}{sentences[0]}.{Style.RESET_ALL} {sentences[1]}"


def ok(message):
    print(colour_first_sentence(message, Fore.GREEN + Style.BRIGHT))


def warn(message):
    print(colour_first_sentence(message, Fore.YELLOW + Style.BRIGHT))


def note(message):
    print(colour_first_sentence(message, Fore.BLACK + Style.BRIGHT))


def error(message):
    print(colour_first_sentence(message, Fore.RED + Style.BRIGHT))
    os.system("pause")
    sys.exit(1)
