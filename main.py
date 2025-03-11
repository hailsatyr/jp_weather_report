import streamlit as st
from hourly_weather import *
import os

MAJ_VERSION = 1
MIN_VERSION = 0

os.makedirs("./reports", exist_ok=True)

st.header(f"Hourly weather data (v{MAJ_VERSION}.{MIN_VERSION})")

selected_pref = st.selectbox("Select target prefecture", [p[0] for p in PREFS], index=None)
selected_date = st.date_input("Select Date", datetime.today() - timedelta(days=1), max_value=datetime.today() - timedelta(days=1))

if selected_pref:
    pref_data = next(p for p in PREFS if p[0] == selected_pref)
else:
    st.stop()

# Form query string
qstring = {
    "prec_no": pref_data[1],
    "block_no": pref_data[2],
    "year": selected_date.year,
    "month": selected_date.month,
    "day": selected_date.day,
    "view": "p1"
}

# Fetch data when button is clicked
if st.button("Fetch Weather Data"):
    filename = f'{pref_data[0].lower().rstrip("prefecture").strip().replace(" ", "_")}_{qstring["year"]}-{qstring["month"]}-{qstring["day"]}.xlsx'
    filepath = f"./reports/{filename}"
    if os.path.exists(filepath):
        st.write("Excel file for this prefecture and date has already been downloaded by someone before.")
        st.write("You can download it directly from the database using button below.")
        with open(filepath, "rb") as f:
            st.download_button("Download Excel File", f, file_name=filename)
    else:
        response = requests.get(url="https://www.data.jma.go.jp/stats/etrn/view/hourly_s1.php", params=qstring)
        st.write(f"Fetching data from: {response.url}")

        if response.status_code == 200:
            lines = []
            for line in response.iter_lines(decode_unicode=True):
                lines.append(line)

            lines_to_write = []
            for line in lines:
                writeln = line
                for word in translate[0]:
                    if word in line:
                        line = line.replace(word, translate[1][translate[0].index(word)])
                lines_to_write.append(line)

            data = StringIO("".join(lines_to_write))
            
            soup = BeautifulSoup(data, "html.parser")
            table = soup.find(id="tablefix1")

            if table:
                df = pd.read_html(StringIO(table.prettify()))[0]
                df.set_index(df.columns[0], inplace=True)

                # Convert to Excel
                df.to_excel(filepath)
                with open(filepath, "rb") as f:
                    st.download_button("Download Excel File", f, file_name=filename)
                st.write(df)
            else:
                st.error("No data found!")
        else:
            st.error("Failed to fetch data!")
