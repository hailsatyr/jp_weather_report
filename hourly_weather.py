import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime,timedelta
from toolbox_python.output import list_columns
from io import StringIO
import os
import subprocess

translate = (("日射量", "全天", "現地", "海面", "降水量", "気温", "湿度", "日照", "時間", "合計", "最大1時間", "最大10分間", "平均", "最高", "最低", "最小", "最大瞬間","最多", "降雪の深さの","最深積雪","風速","風向","最大", "降雪", "積雪", "雪", "露点", "蒸気圧", "温度", "気圧", "天気", "雲量", "視程", "時"), 
             ("Solar radiation", "All sky", "At the site", "At the sea level", "Precipitation", "Temperature", "Humidity", "Sunlight","Hours", "Total", "Highest per hour", "Highest per 10 min", "Average", "Highest", "Lowest","Smallest", "Highest momentary", "Most", "Snow thickness", "The deepest snow point", "Wind velocity", "Wind direction", "Highest", "Snowfall", "Snow accumulation", "Snow", "Dew point", "Atmospheric pressure", "Temperature", "Atmospheric pressure", "Weather", "Cloudiness", "Visibility", "Hour"))

if len(translate[0]) != len(translate[1]):
    raise "Mismatch in dictionary"

def get_prefs():
    prefs = []
    with open("prefs_en", "r") as file:
        lines = file.readlines()
    for line in lines:
        prefecture = line.split(":")[0]
        num = int(line.split(":")[1].split(",")[0])
        block = int(line.split(":")[1].split(",")[1])
        prefs.append([prefecture, num, block])
    return prefs

def prefs_print():
    printlist = []
    for pref in PREFS:
        printlist.append(f"{PREFS.index(pref)}. {pref[0]}")
    print(list_columns(printlist, cols_wide=3))

def get_user_pref():
    prefs_print()
    print("".ljust(35,"-"))
    user = ""
    while True: 
        user = input("Select target prefecture: ")
        if not user.isnumeric() or int(user) < 0 or int(user) > len(PREFS) - 1:
            print(f"Wrong input. Use only numbers 0 to {len(PREFS)-1} to choose prefecture.")
            continue
        else:
            break
    print(f"{PREFS[int(user)][0]} selected.")
    return PREFS[int(user)]

def get_user_date():
    year = month = day = ""
    user = ""
    while True:
        user = input("Enter date in YYYY-MM-DD format (leave empty to choose yesterday): ")
        if user == "":
            # Weather website only provides weather report up to yesterday
            date = datetime.today() - timedelta(days=1)
            break
        else:
            try:
                date = datetime.strptime(user, "%Y-%m-%d")
                if date > datetime.today() - timedelta(days=1):
                    print("Can't select future date.")
                    continue
            except:
                print("Wrong input.")
                continue
            else:
                break
    return date

def form_qstring(prec_no: int, block_no: int, year: int, month: int, day: int):
    qstring = {
        "prec_no": prec_no,
        "block_no": block_no,
        "year": year,
        "month": month,
        "day": day,
        "view": "p1"
    }
    return qstring

def process(qstring, prefname: str):
    filename = f'{prefname.lower().rstrip("prefecture").strip().replace(" ", "_")}_{qstring["year"]}_{qstring["month"]}_{qstring["day"]}.xlsx'
    if os.path.exists(f"./reports/{filename}"):
        print("Report for this date and prefecture already exists!")
        print(f"./reports/{filename}")
        subprocess.Popen(rf'explorer /select,".\reports\{filename}"')
        input("Press any button to exit")
        return
    response = requests.get(url="https://www.data.jma.go.jp/stats/etrn/view/hourly_s1.php", params=qstring)
    print(f"Final URL [{response.status_code}]: ", response.url)
    response.raise_for_status()
    lines = []
    for line in response.iter_lines(decode_unicode=True):
        lines.append(line)

    # with open("hourly.html", "r", encoding="utf-8") as file:
    #     lines = file.readlines()

    lines_to_write = []
    for line in lines:
        writeln = line
        for word in translate[0]:
            if word in line:
                line = line.replace(word, translate[1][translate[0].index(word)])
        lines_to_write.append(line)

    data = StringIO("".join(lines_to_write))

    # with open("translated.html", "w", encoding="utf-8") as file:
    #     file.writelines(lines_to_write)
    # with open("translated.html", "r", encoding="utf-8") as file:
    #     data = file.read()
    # if os.path.exists("translated.html"):
    #     os.remove("translated.html")

    soup = BeautifulSoup(data, "html.parser")
    table = soup.find(id="tablefix1")
    html_table = StringIO(table.prettify())
    
    df = pd.read_html(html_table)[0]
    df.set_index(df.columns[0], inplace=True)

    try:
        df.to_excel(f"./reports/{filename}")
    except Exception as e:
        print("Could not save file!")
        raise e
    else:
        print(f"Successfully saved to ./reports/{filename}")
        subprocess.Popen(rf'explorer /select,".\reports\{filename}"')
        input("Press any button to exit")

global PREFS
PREFS = get_prefs()
if __name__ == '__main__':
    selected_pref = get_user_pref()
    selected_date = get_user_date()
    qstring = form_qstring(selected_pref[1], selected_pref[2], selected_date.year, selected_date.month, selected_date.day)
    #print("Query string: ", qstring)
    process(qstring, selected_pref[0])
