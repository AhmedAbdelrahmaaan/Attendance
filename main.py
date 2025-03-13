import pandas as pd
import streamlit as st
from datetime import datetime as dt
import datetime
from streamlit_js_eval import get_geolocation
from geopy.geocoders import Nominatim
import geopy.distance
from random import randint
import time as ti
import streamlit_authenticator as stauth
from streamlit_gsheets import GSheetsConnection
import pytz
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np
#import pyautogui
from streamlit_option_menu import option_menu
from streamlit_extras.switch_page_button import switch_page
from st_pages import Page, show_pages,hide_pages
from streamlit_extras.switch_page_button import switch_page
import xlsxwriter
from io import BytesIO
from sklearn.cluster import KMeans, AgglomerativeClustering
import io
import matplotlib.pyplot as plt


if 'code' not in st.session_state:
    st.session_state.code = ''

def submit():
    st.session_state.code = st.session_state.widget
    st.session_state.widget = ''

if 'x' not in st.session_state:
     st.session_state['x'] = 0

st.session_state.store = ""
# st.set_page_config(page_title="Login Page")

# show_pages([Page("main.py","Login Page")])

#Header
col1, col2 = st.columns([1, 7])
with col1:
    st.image("Smart FieldLogo.jpg",width=100)
with col2:
    st.title("Smart Field Appliaction")


#Time Capture Data
time_format = "%Y-%m-%d  %H:%M:%S.%f"
Now = dt.now().replace(tzinfo=None)
utc = dt.utcnow().replace(tzinfo=pytz.UTC).replace(tzinfo=None)
timediff = datetime.datetime.now(pytz.timezone('Africa/Cairo')).replace(tzinfo=None) - utc
Now = datetime.datetime.now(pytz.timezone('Africa/Cairo'))
st.session_state.date = str(Now.date())


#Load Employee Data_Function
#@st.cache_data
def fetch_and_clean_data():
    conn = st.experimental_connection("gsheets", type=GSheetsConnection)

    Employee_df = conn.read(worksheet="Sheet1",
                   ttl="10s",
                   usecols=[0, 1, 2],
                   nrows=100)
    return Employee_df

#@st.cache_data
def Attendance_Data():
    conn = st.experimental_connection("gsheets", type=GSheetsConnection)

    Employee_df = conn.read(worksheet="Sheet2",
                   ttl="10s",
                   usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8,9,10],
                   nrows=1000)
    return Employee_df

# Main Page
selected = option_menu(menu_title=None,options=["Employee","Company","IFM Route"],icons=["person-vcard-fill","building","building"],orientation="horizontal")

if selected == "Employee":
    #Login Details
    text = st.empty()
    code = text.text_input("****Enter your code****",max_chars=4,key="widget",on_change=submit)
    if  st.session_state.code != "":
        df = fetch_and_clean_data()
        if int(st.session_state.code) not in df["Employee Code"].values:
            st.error("Wrong Code! Renter your Code")

        else:
            placeholder1, placeholder2, placeholder3, placeholder4 = st.empty(), st.empty(), st.empty(), st.empty()
            st.session_state.name = df[df["Employee Code"] == int( st.session_state.code)]["Employee Name"].values[0]
            Project = df[df["Employee Code"] == int( st.session_state.code)]["Project"].values[0]
            placeholder1.subheader("**Please Check and confirm your data!**")
            d = {'Name': [st.session_state.name ], 'Code': [ st.session_state.code], 'Project': [Project]}
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
                if st.checkbox("Check my location"):
                    try:
                        user_agent = 'My App {}'.format(randint(1, 99999))
                        geolocator = Nominatim(user_agent=user_agent)
                        loc = get_geolocation()
                        ti.sleep(1)
                        latitude = loc['coords']['latitude']
                        longitude = loc['coords']['longitude']
                        actual_coordinates = "{},{}".format(latitude, longitude)
                        location = geolocator.reverse(actual_coordinates)
                        address = location.raw['address']
                        # Target_Location = employees[employee_code][2]
                        # Distance = round(geopy.distance.geodesic(Target_Location, actual_coordinates).km, 2)
                        st.write(actual_coordinates, " \n ", location)
                        st.session_state.store = st.text_input("****Enter store name****")
                    except:
                        st.write("Loading.................")
                    # show_pages([Page("Login_Page.py", "Login Page"), Page("Pages\main.py", "Survey")])
                    # switch_page("Survey")
                    if st.session_state.store !="":
                        if st.button("Submit"):
                            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                        #     # Write
                        #create this on secrects / TOML
                        ## google_service_account = {"type" = "service_account", "project_id", AND_SO_ON}
                        # Load credentials from Streamlit secrets
                            google_service_account = st.secrets["google_service_account"]                        # google_service_account_info = st.secrets['google_service_account']
                        # creds = ServiceAccountCredentials.from_json_keyfile_dict(google_service_account_info, scope)
                            creds = ServiceAccountCredentials.from_json_keyfile_dict(google_service_account, scope)

                        #     creds = ServiceAccountCredentials.from_json_keyfile_name('gapi.json', scope)
                            client = gspread.authorize(creds)
                            sh = client.open('Elios APP').worksheet('Sheet2')
                            row = [st.session_state.code, st.session_state.name,Project,st.session_state.date,st.session_state.store,str(location),str(utc),str(Now),str(timediff),latitude,longitude]
                            sh.append_row(row)
                            st.success('This is a success message!', icon="✅")
                            ti.sleep(2)
                            st.session_state.code = ""
                            st._rerun()
                            

            elif nonConfirm:
                st.session_state.code = ""
                st._rerun()
                st.write("Please Re-enter your code")

elif selected == "Company":
    text1, text2 = st.empty(), st.empty()
    Companynameoriginal = "IFM"
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
        Attendance['Date'] =  Attendance['Date'].dt.date

        DATEfrom = st.date_input("From")
        DATETo = st.date_input("To")
        if DATEfrom>DATETo:
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
            st.download_button("Dowmload Attendance Sheet", data=df_xlsx, file_name='Attendance from {} to {}.xlsx'.format(DATEfrom,DATETo),
                               mime="application/vnd.ms-excel")

elif selected == "IFM Route":
    text1, text2 = st.empty(), st.empty()
    Companynameoriginal = "IFM"
    Passwordoriginal = "1234"

    Companyname = text1.text_input("****Company Name****", max_chars=20, key="3")
    Password = text2.text_input("****Password****", max_chars=20, key="4",type='password')

    if Companyname == Companynameoriginal and Password == Passwordoriginal:
        text1.empty()
        text2.empty()
        N_Routes = st.number_input("Enter Number of Routes",step=1)
        working_days = st.multiselect('What are working days?',['Saturday', 'Sunday', 'Monday', 'Tuesday','Wednesday','Thursday','Friday'])
        working_days_dic = {}
        for i in range(len(working_days)):
            working_days_dic[i] = working_days[i]

        Route_dic = {}
        for i in range(N_Routes):
            Route_dic[i] = f'Route_{i+1}'

        storelist = st.file_uploader("Upload your storelist")
        if storelist is not  None:
            try:
                storelist_df = pd.read_csv(storelist)
            except:
                storelist_df = pd.read_excel(storelist,engine="openpyxl")

            from IFMROUTE import  IFMROUTE
            storelist_df = IFMROUTE(storelist_df, N_Routes, working_days)
            working_Days_color = (storelist_df['working_Days'] + 1).copy()
            storelist_df['working_Days'] = storelist_df['working_Days'].replace(working_days_dic)
            route_color = (storelist_df['Route']+1).copy()
            storelist_df['Route'] = storelist_df['Route'].replace(Route_dic)
            storelist_df['working_Days_2'] = storelist_df['working_Days'].copy()
            idx = storelist_df.columns.tolist()
            index_n = idx.index('working_Days')
            idx.pop(index_n)
            df_pivoted = storelist_df.assign(Value=1).pivot(index= idx,columns='working_Days', values='Value').fillna(0).astype(int)
            # st.write(df_pivoted)





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
            ax.legend(*scatter.legend_elements(),loc="upper left", title="Routes")
            # ax.add_artist(legend1)
            ax.set_title("Routes in the selected area")
            st.pyplot(fig)
            st.write(storelist_df['Route'].value_counts().sort_index())


            st.download_button(
                label="Download Excel",
                data=download_excel(df_pivoted),
                file_name="storelist routes.xlsx",
                key="download_button"
            )
