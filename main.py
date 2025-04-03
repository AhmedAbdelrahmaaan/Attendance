import pandas as pd
import streamlit as st
from datetime import datetime as dt
import datetime
from streamlit_js_eval import get_geolocation
from geopy.geocoders import Nominatim
import geopy.distance
from random import randint
import time as ti
import gspread
from google.oauth2.service_account import Credentials
import pytz
import numpy as np
from streamlit_option_menu import option_menu
from io import BytesIO
import matplotlib.pyplot as plt
import io

# Initialize session state variables
if 'code' not in st.session_state:
    st.session_state.code = ''

if 'x' not in st.session_state:
    st.session_state['x'] = 0

st.session_state.store = ""


# Define the submit function
def submit():
    st.session_state.code = st.session_state.widget
    st.session_state.widget = ''


# Header
col1, col2 = st.columns([1, 7])
with col1:
    st.image("ELIOSLOGO.png", width=100)
with col2:
    st.title("ELIOS Market Scan Application")

# Time Capture Data
time_format = "%Y-%m-%d  %H:%M:%S.%f"
Now = dt.now().replace(tzinfo=None)
utc = dt.utcnow().replace(tzinfo=pytz.UTC).replace(tzinfo=None)
timediff = datetime.datetime.now(pytz.timezone('Africa/Cairo')).replace(tzinfo=None) - utc
Now = datetime.datetime.now(pytz.timezone('Africa/Cairo'))
st.session_state.date = str(Now.date())


# Function to get Google Sheets connection
def get_google_sheets_connection():
    try:
        # Load credentials from Streamlit secrets
        google_service_account = st.secrets["google_service_account"]

        # Define the scope
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

        # Create credentials
        creds = Credentials.from_service_account_info(google_service_account, scopes=scope)

        # Authorize the client
        client = gspread.authorize(creds)

        return client
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return None


# Function to fetch employee data
@st.cache_data(ttl=600)
def fetch_and_clean_data():
    try:
        client = get_google_sheets_connection()
        if client:
            # Open the Google Sheet
            sheet = client.open("Elios APP").worksheet("Sheet1")

            # Fetch data
            data = sheet.get_all_records()
            df = pd.DataFrame(data)

            return df
        else:
            return pd.DataFrame()  # Return an empty DataFrame if connection fails
    except Exception as e:
        st.error(f"Error fetching data from Google Sheets: {e}")
        return pd.DataFrame()


# Function to fetch attendance data
def Attendance_Data():
    try:
        client = get_google_sheets_connection()
        if client:
            # Open the Google Sheet
            sheet = client.open("Elios APP").worksheet("Sheet2")

            # Fetch data
            data = sheet.get_all_records()
            df = pd.DataFrame(data)

            return df
        else:
            return pd.DataFrame()  # Return an empty DataFrame if connection fails
    except Exception as e:
        st.error(f"Error fetching attendance data from Google Sheets: {e}")
        return pd.DataFrame()


# Function to write data to Google Sheets
def write_to_google_sheets(row_data):
    try:
        client = get_google_sheets_connection()
        if client:
            # Open the Google Sheet
            sheet = client.open("Elios APP").worksheet("Sheet2")

            # Append the row
            sheet.append_row(row_data)
            st.success("Data successfully written to Google Sheets!")
        else:
            st.error("Failed to connect to Google Sheets.")
    except Exception as e:
        st.error(f"Error writing to Google Sheets: {e}")


# Main Page
selected = option_menu(menu_title=None, options=["Employee", "Company", "Elios Route"],
                       icons=["person-vcard-fill", "building", "building"], orientation="horizontal")

if selected == "Employee":
    # Login Details
    text = st.empty()
    code = text.text_input("****Enter your code****", max_chars=4, key="widget", on_change=submit)
    if st.session_state.code != "":
        df = fetch_and_clean_data()
        if int(st.session_state.code) not in df["Employee Code"].values:
            st.error("Wrong Code! Re-enter your Code")
        else:
            placeholder1, placeholder2, placeholder3, placeholder4 = st.empty(), st.empty(), st.empty(), st.empty()
            st.session_state.name = df[df["Employee Code"] == int(st.session_state.code)]["Employee Name"].values[0]
            Project = df[df["Employee Code"] == int(st.session_state.code)]["Project"].values[0]
            placeholder1.subheader("**Please Check and confirm your data!**")
            d = {'Name': [st.session_state.name], 'Code': [st.session_state.code], 'Project': [Project]}
            emp_df = pd.DataFrame(data=d, index=[""])
            Employee_data = placeholder2.table(emp_df[0:])

            col3, col4 = st.columns([1, 1])
            with col3:
                Confirm = placeholder3.checkbox("Confirmed ✔")
            with col4:
                nonConfirm = placeholder4.checkbox("Not Confirmed ❌")

            if Confirm:
                placeholder3.empty()
                placeholder4.empty()
                st.session_state.location = "NA"
                get_location = st.checkbox("Check my location")
                actual_coordinates = "Not Available"

                if get_location:
                    try:
                        user_agent = f"MyApp{randint(1, 99999)}"
                        geolocator = Nominatim(user_agent=user_agent)
                        loc = get_geolocation()
                        ti.sleep(2)
                        latitude = loc['coords']['latitude']
                        longitude = loc['coords']['longitude']
                        actual_coordinates = f"{latitude},{longitude}"
                        location = geolocator.reverse(f"{latitude},{longitude}", timeout=10)
                        st.session_state.location = location
                        st.write(actual_coordinates, " \n ", location)
                    except Exception as e:
                        st.error(f"Error getting location: {e}")

                st.text_input("📍 Coordinates:", actual_coordinates, disabled=True)

                # linkbutton
                st.markdown(
                    '<a href="https://forms.gle/veLwxXtN2irKPLmR9" target="_blank">'
                    '<button style="background-color:#4CAF50; color:white; padding:10px 24px; border:none; '
                    'border-radius:5px; font-size:16px; cursor:pointer;">📝 Open Survey Form</button></a>',
                    unsafe_allow_html=True
                )


                with st.form("survey_form"):

                    st.session_state.store = st.text_input("Enter store name")

                    # 1. التاريخ (Date)
                    st.session_state.visitdate = st.date_input("التاريخ")

                    # 2. اسم المراجع (Reviewer's Name)
                    st.session_state.reviewer_name = st.text_input("اسم المراجع")

                    # 3. المحافظة (Governorate)
                    st.session_state.governorate = st.text_input("المحافظة")

                    # 4. المركز (Center)
                    st.session_state.center = st.text_input("المركز")

                    # 5. المنطقة (Region)
                    st.session_state.region = st.text_input("المنطقة")

                    # 6. العنوان بالتفصيل (Detailed Address)
                    st.session_state.detailed_address = st.text_input("العنوان بالتفصيل")

                    # 7. علامة مميزة (Landmark)
                    st.session_state.landmark = st.text_input("علامة مميزة")

                    # # 8. اسم المحل (Store Name)
                    # store_name = st.text_input("اسم المحل")

                    # 9. اسم المسؤل (Responsible Person's Name)
                    st.session_state.responsible_name = st.text_input("اسم المسؤل")

                    # 10. رقم المسؤل (Responsible Person's Number)
                    st.session_state.responsible_number = st.text_input("رقم المسؤل")

                    # 11. حجم المحل (Store Size)
                    st.session_state.store_size = st.radio("حجم المحل", ["كبير", "متوسط", "صغير"])

                    # 12. هل تعمل في منتجات اليوس؟ (Do you work with Yous products?)
                    st.session_state.work_with_yous = st.radio("هل تعمل في منتجات اليوس؟", ["نعم", "لا"])

                    # 12. هل تعمل في منتجات اليوس؟ (Do you work with Yous products?)
                    st.session_state.work_with_anasia = st.radio("هل تعمل مع أناسيا؟", ["نعم", "لا"])


                  # 13. في حالة الاجابة ب لا هل عندك سجل تجاري وبطاقة ضريبية سارية ومحتاج تشتغل بيهم ؟
                    st.session_state.has_commercial_register = st.radio(
                        "في حالة الاجابة ب لا هل عندك سجل تجاري وبطاقة ضريبية سارية ومحتاج تشتغل بيهم ؟",
                        ["نعم", "لا", "متعامل فعلا"])

                    
                    # 14. عندك ايه من اليوس ليد بالب ؟ (Which Yous LED bulbs do you have?)
                    st.session_state.yous_led_bulbs = st.multiselect(
                        "عندك ايه من اليوس ليد بالب ؟",
                        ["9W", "12W", "15W", "18W", "23W", "30W", "45W", "لا يعمل"]
                    )

                    # 15. عندك ايه من اليوس الليد تيوب ؟ (Which Yous LED tubes do you have?)
                    st.session_state.yous_led_tubes = st.multiselect(
                        "عندك ايه من اليوس الليد تيوب ؟",
                        ["60 CM", "120 CM", "لا يعمل"]
                    )

                    # 16. عندك ايه من مشتركات اليوس ؟ (Which Yous sockets do you have?)
                    st.session_state.yous_sockets = st.multiselect(
                        "عندك ايه من مشتركات اليوس ؟",
                        ["بسلك", "بدون سلك", "لا يعمل"]
                    )

                    # 17. عندك ايه من اضاءة اليوس ؟ (Which Yous lighting do you have?)
                    st.session_state.yous_lighting = st.multiselect(
                        "عندك ايه من اضاءة اليوس ؟",
                        ["داون لايت", "سبوت لايت", "كاندل", "كاسة", "لا يعمل"]
                    )

                    # 18. عندك قواطع وشريط لحام اليوس ؟ (Do you have Yous breakers and soldering tape?)
                    st.session_state.yous_breakers_tape = st.multiselect(
                        "عندك قواطع وشريط لحام اليوس ؟",
                        ["قواطع", "شريط لحام", "لا يعمل"]
                    )

                    # 19. هل تعمل توريدات ؟ (Do you work in supplies?)
                    st.session_state.work_in_supplies = st.radio(
                        "هل تعمل توريدات ؟",
                        ["نعم", "لا"]
                    )

                    # 20. هل في مواد دعاية ل اليوس ؟ (Are there promotional materials for Yous?)
                    st.session_state.yous_promo_materials = st.multiselect(
                        "هل في مواد دعاية ل اليوس ؟",
                        ["يافطة", "لايت بوكس", "ستاند داون لايت", "لا يوجد"]
                    )

                    # 21. يوجد استاند اليوس ؟ (Is there a Yous stand?)
                    st.session_state.has_yous_stand = st.radio(
                        "هل يوجد استاند اليوس ؟",
                        ["جيد", "يحتاج صيانة", "في المخزن", "لا يوجد"]
                    )

                    # 23. التعليق ؟ (Comments?)
                    st.session_state.comments = st.text_area("التعليق ؟")

                    submitted = st.form_submit_button("Submit")

                    if submitted:
                        required_data = [st.session_state.code,
                                         st.session_state.name,
                                         Project,
                                         st.session_state.date,
                                         st.session_state.store,
                                         location,
                                         utc,
                                         Now,
                                         timediff,
                                         latitude,
                                         longitude,
                                         st.session_state.visitdate,
                                         st.session_state.reviewer_name,
                                         st.session_state.governorate,
                                         st.session_state.center,
                                         st.session_state.region,
                                         st.session_state.detailed_address,
                                         st.session_state.landmark,
                                         st.session_state.responsible_name,
                                         st.session_state.responsible_number,
                                         st.session_state.store_size,
                                         st.session_state.work_with_yous,                                                                          
                                         st.session_state.work_with_anasia,

                                         st.session_state.has_commercial_register,
                                         st.session_state.yous_led_bulbs,
                                         st.session_state.yous_led_tubes,
                                         st.session_state.yous_sockets,
                                         st.session_state.yous_lighting,
                                         st.session_state.yous_breakers_tape,
                                         st.session_state.work_in_supplies,
                                         st.session_state.yous_promo_materials,
                                         st.session_state.has_yous_stand
                                         ]

                        if all(required_data):
                            row = [str(value) if value else "" for value in required_data] + [st.session_state.comments]
                            write_to_google_sheets(row)
                            ti.sleep(2)
                            st.session_state.code = ""
                            st._rerun()
                        else:
                            st.warning("Please fill in all required fields.")

            elif nonConfirm:
                st.session_state.code = ""
                st._rerun()
                st.warning("Please re-enter your code.")

elif selected == "Company":
    text1, text2 = st.empty(), st.empty()
    Companynameoriginal = "Elios"
    Passwordoriginal = "1234"

    Companyname = text1.text_input("****Company Name****", max_chars=20, key="3")
    Password = text2.text_input("****Password****", max_chars=20, key="4")

    if Companyname == Companynameoriginal and Password == Passwordoriginal:
        text1.empty()
        text2.empty()
        st.success("Login Success")
        allemp = fetch_and_clean_data().dropna(subset=['Employee Code'])
        Attendance = Attendance_Data().dropna(subset=['Employee Code'])
        Attendance['Date'] = pd.to_datetime(Attendance['Date'])
        Attendance['Date'] = Attendance['Date'].dt.date

        DATEfrom = st.date_input("From")
        DATETo = st.date_input("To")
        if DATEfrom > DATETo:
            st.error("Date to should be after date from")
        else:
            datebaesddf = Attendance[(Attendance["Date"] >= DATEfrom) & (Attendance["Date"] <= DATETo)]
            aaa = datebaesddf.merge(allemp, on=["Employee Code", "Employee Name", "Project"], how="outer")
            st.write(aaa)


            def to_excel(df):
                output = BytesIO()
                writer = pd.ExcelWriter(output, engine='xlsxwriter')
                df.to_excel(writer, index=False, sheet_name='Sheet1')
                workbook = writer.book
                worksheet = writer.sheets['Sheet1']
                format1 = workbook.add_format({'num_format': '0.00'})
                worksheet.set_column('A:A', None, format1)
                writer.save()
                processed_data = output.getvalue()
                return processed_data


            df_xlsx = to_excel(aaa)
            st.download_button("Download Attendance Sheet", data=df_xlsx,
                               file_name='Attendance from {} to {}.xlsx'.format(DATEfrom, DATETo),
                               mime="application/vnd.ms-excel")

elif selected == "Elios Route":
    text1, text2 = st.empty(), st.empty()
    Companynameoriginal = "Elios"
    Passwordoriginal = "1234"

    Companyname = text1.text_input("****Company Name****", max_chars=20, key="3")
    Password = text2.text_input("****Password****", max_chars=20, key="4", type='password')

    if Companyname == Companynameoriginal and Password == Passwordoriginal:
        text1.empty()
        text2.empty()
        N_Routes = st.number_input("Enter Number of Routes", step=1)
        working_days = st.multiselect('What are working days?',
                                      ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
        working_days_dic = {}
        for i in range(len(working_days)):
            working_days_dic[i] = working_days[i]

        Route_dic = {}
        for i in range(N_Routes):
            Route_dic[i] = f'Route_{i + 1}'

        storelist = st.file_uploader("Upload your storelist")
        if storelist is not None:
            try:
                storelist_df = pd.read_csv(storelist)
            except:
                storelist_df = pd.read_excel(storelist, engine="openpyxl")

            from IFMROUTE import IFMROUTE

            storelist_df = IFMROUTE(storelist_df, N_Routes, working_days)
            working_Days_color = (storelist_df['working_Days'] + 1).copy()
            storelist_df['working_Days'] = storelist_df['working_Days'].replace(working_days_dic)
            route_color = (storelist_df['Route'] + 1).copy()
            storelist_df['Route'] = storelist_df['Route'].replace(Route_dic)
            storelist_df['working_Days_2'] = storelist_df['working_Days'].copy()
            idx = storelist_df.columns.tolist()
            index_n = idx.index('working_Days')
            idx.pop(index_n)
            df_pivoted = storelist_df.assign(Value=1).pivot(index=idx, columns='working_Days', values='Value').fillna(
                0).astype(int)


            def download_excel(df_pivoted):
                # Save the pivoted DataFrame to an Excel file
                excel_file = io.BytesIO()
                df_pivoted.to_excel(excel_file, index=True, header=True)
                excel_file.seek(0)
                return excel_file


            x = storelist_df["longitude"]
            y = storelist_df["latitude"]
            c = storelist_df['Route']
            fig, ax = plt.subplots()
            scatter = ax.scatter(storelist_df["longitude"], storelist_df["latitude"], c=route_color, cmap='viridis')
            ax.legend(*scatter.legend_elements(), loc="upper left", title="Routes")
            ax.set_title("Routes in the selected area")
            st.pyplot(fig)
            st.write(storelist_df['Route'].value_counts().sort_index())

            st.download_button(
                label="Download Excel",
                data=download_excel(df_pivoted),
                file_name="storelist routes.xlsx",
                key="download_button"
            )
