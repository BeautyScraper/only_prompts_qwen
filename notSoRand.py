import random
import re
import os
from pathlib import Path

# 'files' folder is located next to this script, so it works regardless of the
# current working directory (no os.chdir needed on Colab/Linux).
FILES_DIR = Path(__file__).resolve().parent / 'files'

BRACKET_PATTERN = re.compile(r"\[([^\[]*?)\]")
FREQ_IN_NAME_PATTERN = re.compile(r"\((\d+)\)")


def _resolve_ci(path: Path) -> Path:
    """
    Case-insensitive path lookup.
    Windows ignores letter case in file names, Linux does not, so a reference like
    [Hair] must still find 'hair.txt'. If an exact match exists it is used as-is.
    """
    if path.exists() or path == path.parent:
        return path
    parent = _resolve_ci(path.parent)
    if parent.is_dir():
        wanted = path.name.lower()
        for child in parent.iterdir():
            if child.name.lower() == wanted:
                return child
    return parent / path.name


def preprocess_lines(lines):
    updated_lines = []
    for line in lines:
        if '#' in line:
            try:
                get_freq = int(line.split('#')[0])
            except ValueError:
                get_freq = 1
            for c in range(get_freq):
                updated_lines.append(line.split('#')[1])
        else:
            updated_lines.append(line)
    return updated_lines


def random_line(npath):
    newpath = _resolve_ci(FILES_DIR / Path(npath))
    dir_candidate = _resolve_ci(newpath.with_name(newpath.stem))
    if dir_candidate.is_dir():
        newpath = dir_candidate
        files = []
        for f in newpath.iterdir():
            if f.is_file() and f.suffix == '.txt':
                freq = 1
                try:
                    m = FREQ_IN_NAME_PATTERN.search(f.name)
                    if m:
                        freq = int(m.group(1))
                except Exception:
                    pass
                for _ in range(freq):
                    files.append(f)

        if files:
            selected_file = random.choice(files)
            return return_entire_string_after_replacing_patterns(selected_file)[0], selected_file.stem

    if newpath.is_file():
        return randomLine_helper(newpath.with_suffix('.txt').name)[0], None
    else:
        return newpath.stem, None


def preprocess_content(content):
    pattern = re.compile(r"\*\*(\d+)")
    for match in pattern.finditer(content):
        content = content[:match.start()] + content[match.end():]
    return content


def return_entire_string_after_replacing_patterns(filepath: Path):
    with open(filepath, "r", encoding="utf-8", errors="replace") as file:
        content = file.read()

        # Replace patterns like [something] recursively
        while BRACKET_PATTERN.search(content):
            match = BRACKET_PATTERN.search(content)
            stringfromfile = match.group(1)
            if '||' not in stringfromfile and ' ' not in stringfromfile:
                try:
                    replacement = random_line(stringfromfile + ".txt")[0]
                except Exception as e:
                    # No debugger on Colab/headless: log and fall back to the raw text
                    print(f"Error resolving [{stringfromfile}]: {e}")
                    replacement = stringfromfile
            else:
                replacement = random.choice(stringfromfile.split('||'))
            content = content[:match.start()] + replacement + content[match.end():]
        return content.rstrip('\n'), None


def randomLine_helper(fileName="test.txt"):
    file_path = _resolve_ci(FILES_DIR / fileName)
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as inF:
            try:
                allLines = inF.readlines()
                allLines = preprocess_lines(allLines)
                selectedLine = random.choice(allLines)
            except Exception:
                selectedLine = 'Kuch Nahi'

            # (Windows-only 'start' call to open the file in an editor was removed)

            while BRACKET_PATTERN.search(selectedLine):
                stringfromfile = BRACKET_PATTERN.search(selectedLine)[1]
                if '||' not in stringfromfile:
                    replaceMentStr = random_line(stringfromfile + ".txt")[0]
                else:
                    replaceMentStr = random.choice(stringfromfile.split('||'))
                # lambda avoids backslash/group interpretation in the replacement text
                selectedLine = BRACKET_PATTERN.sub(lambda _m: replaceMentStr, selectedLine, count=1)
    except (FileNotFoundError, IndexError):
        if len(fileName.split(" ")) == 1:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()
        selectedLine = fileName.split(".")[0]
    return selectedLine.rstrip('\n'), None


def main():
    FILES_DIR.mkdir(parents=True, exist_ok=True)
    return random_line('qwen')[0]


if __name__ == '__main__':
    FILES_DIR.mkdir(parents=True, exist_ok=True)
    line = random_line("qwen")[0]

    print(line)
