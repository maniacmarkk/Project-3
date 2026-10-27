from pathlib import Path
import shutil

def find_direct_files(directory: Path) -> list[Path]:
    """Returns files directly in the directory, sorted by filename."""
    file_list = []
    try:
        for item in directory.iterdir():
            try:
                if item.is_file():
                    file_list.append(item)
            except OSError:
                continue
    except OSError:
        pass

    file_list.sort(key=file_name)
    return file_list


def file_name(item: Path) -> str:
    """Returns the name of the given path."""
    return item.name

def find_direct_subdirectories(directory: Path) -> list[Path]:
    """Returns direct subdirectories, sorted by name."""
    subdirectory_list = []
    try:
        for item in directory.iterdir():
            try:
                if item.is_dir():
                    subdirectory_list.append(item)
            except OSError:
                continue
    except OSError:
        pass

    subdirectory_list.sort(key=file_name)
    return subdirectory_list

def find_all_files(directory: Path) -> list[Path]:
    """Recursively returns files in the required directory and filename order."""
    all_files = find_direct_files(directory)
    all_folders = find_direct_subdirectories(directory)
    for item in all_folders:
        all_files.extend(find_all_files(item))
    return all_files

def read_search_location() -> tuple[str, Path]:
    """Reads a valid search command and directory, reporting invalid input."""
    while True:
        inquiry = input()
        inquiry_list = inquiry.split(' ', 1)
        if len(inquiry_list) <= 1:
            print('ERROR')
            continue
        if inquiry_list and (inquiry_list[0] != 'R' and inquiry_list[0] != 'D'):
            print('ERROR')
            continue
        if len(inquiry_list) == 2 and inquiry_list[1].strip() == '':
            print('ERROR')
            continue
        if not Path(inquiry_list[1]).is_dir():
            print('ERROR')
            continue
        break

    return inquiry_list[0], Path(inquiry_list[1])

def filter_by_name(files: list[Path], name: str) -> list[Path]:
    """Returns files whose names exactly match the given name."""
    new_list = []
    for item in files:
        if file_name(item) == name:
            new_list.append(item)
    return new_list

def filter_by_extension(files: list[Path], extension: str) -> list[Path]:
    """Returns files matching the extension, with or without a leading dot."""
    new_list = []
    if extension[0] != '.':
        modified_extension = '.' + extension
    else:
        modified_extension = extension
    for item in files:
        if modified_extension == item.suffix:
            new_list.append(item)
    return new_list


def filter_by_size(files: list[Path], comparison: str, threshold: int) -> list[Path]:
    """Returns files whose byte sizes satisfy the comparison and threshold."""
    new_list = []
    for item in files:
        try:
            size = item.stat().st_size
            if comparison == '<' and size < threshold:
                new_list.append(item)
            elif comparison == '>' and size > threshold:
                new_list.append(item)
        except OSError:
            continue
    return new_list

def filter_by_text(files: list[Path], text: str) -> list[Path]:
    """Returns readable text files containing the given text."""
    new_list = []
    for item in files:
        file = None
        try: 
            file = item.open('r')
            line_list = file.readlines()
            for line in line_list:
                if text in line:
                    new_list.append(item)
                    break
        except (UnicodeDecodeError, OSError):
            continue
        finally:
            if file is not None:
                file.close()
    return new_list

def read_search_characteristic() -> tuple[str, str | int | None]:
    """Reads a valid search characteristic and its argument."""
    while True:
        command = input()
        valid_commands = ['A', 'N', 'E', 'T', '<', '>']
        if command and command[0] in valid_commands:
            first = command[0]
            if command.strip() == 'A' and len(command) == 1:
                return 'A', None
            if first == 'N' and len(command.strip()) > 1 and command[1] == ' ':
                return 'N', command[2:]
            if first == 'T' and len(command.strip()) > 1 and command[1] == ' ':
                return 'T', command[2:]
            if first == 'E' and len(command.strip()) > 1 and command[1] == ' ':
                return 'E', command[2:]
            if first == '<' and len(command) > 1 and command[1] == ' ':
                try:
                    number = int(command[2:])
                    if number >= 0:
                        return '<', number
                except (ValueError, TypeError):
                    pass
            if first == '>' and len(command) > 1 and command[1] == ' ':
                try:
                    number = int(command[2:])
                    if number >= 0:
                        return '>', number
                except (ValueError, TypeError):
                    pass
        print('ERROR')


def read_action() -> str:
    """Reads a valid action command, reporting invalid input."""
    while True:
        action = input()
        valid_actions = ['F', 'T', 'D']
        if action in valid_actions:
            return action
        print('ERROR')

def print_first_lines(files: list[Path]) -> None:
    """Prints each file's first line, or NOT TEXT if decoding fails."""
    for item in files:
        file = None
        try:
            file = item.open('r')
            line = file.readline()
            print(line.rstrip('\n'))
        except UnicodeDecodeError:
            print('NOT TEXT')
        except OSError:
            continue
        finally:
            if file is not None:
                file.close()

def duplicate_files(files: list[Path]) -> None:
    """Copies each file to the same directory with .dup appended to its name."""
    for file in files:
        try:
            new_name = file.name + '.dup'
            duplicate_file = file.with_name(new_name)
            shutil.copyfile(file, duplicate_file)
        except OSError:
            continue

def touch_files(files: list[Path]) -> None:
    """Updates each file's modification time to the current time."""
    for file in files:
        try:
            file.touch()
        except OSError:
            continue

def main() -> None:
    """Finds files, filters them, and performs the requested action."""
    command, directory = read_search_location()
    if command == 'D':
        files = find_direct_files(directory)
    elif command == 'R':
        files = find_all_files(directory)
    for item in files:
        print(item)
    characteristic, argument = read_search_characteristic()
    if characteristic == 'A':
        interesting_files = files
    elif characteristic == 'N':
        interesting_files = filter_by_name(files, str(argument))
    elif characteristic == 'T':
        interesting_files = filter_by_text(files, str(argument))
    elif characteristic == 'E':
        interesting_files = filter_by_extension(files, str(argument))
    elif characteristic == '>' or characteristic == '<':
        interesting_files = filter_by_size(files, characteristic, int(argument))
    if interesting_files:
        for item in interesting_files:
            print(item)
    else:
        return
    action = read_action()
    if action == 'F':
        print_first_lines(interesting_files)
    elif action == 'D':
        duplicate_files(interesting_files)
    elif action == 'T':
        touch_files(interesting_files)


if __name__ == '__main__':
    main()