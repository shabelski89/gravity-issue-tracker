import os
import re
from datetime import datetime


def flatten(list_of_lists):
    for item in list_of_lists:
        try:
            yield from flatten(item)
        except TypeError:
            if item is not None:
                yield item


def get_issue_from_message(args: str):
    """Return issue number from message with command"""
    try:
        command, issue, *text = args.split()
        issue_number = int(issue)
        return issue_number
    except ValueError:
        return None


def get_command_from_message(message: str):
    """Return command from message with command"""
    command, *_ = message.split()
    return command.strip('/')


def get_numbers_from_text(text: str):
    """Return all number from text"""
    return [int(n) for n in re.findall(r'\d+', text)]


def get_timestamp(dt: datetime = None):
    """Return int unix timestamp"""
    if dt is None:
        dt = datetime.now()
    return int(datetime.timestamp(dt))


def get_filename(prefix: str = 'image', ext: str = 'png'):
    """Return full path to file"""
    try:
        os.makedirs(prefix, exist_ok=True)
    except Exception as E:
        print(E)
    full_file_path = os.path.join(os.getcwd(), prefix, f'{prefix}_{get_timestamp()}.{ext}')
    return full_file_path


def get_route_to_root_from_child(identifier: int, list_of_tuples: list):
    """Return sorted list message chain from child message"""
    result = []
    if identifier is None or identifier in result:
        return

    for p, c in list_of_tuples:
        if p == identifier and c is not None:
            result.append(c)
            index = list_of_tuples.index((p, c))
            yield from get_route_to_root_from_child(c, list_of_tuples[:index])
    if result:
        yield result
