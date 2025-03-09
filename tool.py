import re
def parse_prefs():
    with open("prefs", "r", encoding="utf-8") as file:
        lines = file.readlines()
    for line in lines:
        match = re.search('alt=\"(.+)\" coords.+prec_no=(\d+)', line)
        if match:
            print(f"{match.group(1)}:{match.group(2)}")
        else:
            print("No match", line)

parse_prefs()
