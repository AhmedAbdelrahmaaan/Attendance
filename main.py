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

if 'something' not in st.session_state:
    st.session_state.something = ''

def submit():
    st.session_state.something = st.session_state.widget
    st.session_state.widget = ''

if 'x' not in st.session_state:
     st.session_state['x'] = 0

st.set_page_config(page_title="Login Page")

show_pages([Page("main.py","Login Page")])

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
timediff = Now - utc
st.session_state.date = str(Now.date())


#Load Employee Data_Function
@st.cache_data
def fetch_and_clean_data():
    conn = st.experimental_connection("gsheets", type=GSheetsConnection)

    Employee_df = conn.read(worksheet="Sheet1",
                   ttl="10s",
                   usecols=[0, 1, 2],
                   nrows=5)
    return Employee_df


# Main Page
selected = option_menu(menu_title=None,options=["Employee","Company"],icons=["person-vcard-fill","building"],orientation="horizontal")

if selected == "Employee":
    df = fetch_and_clean_data()
    #Login Details
    text = st.empty()
    code = text.text_input("****Enter your code****",max_chars=4,key="widget",on_change=submit)
    if  st.session_state.something != "":
        if int(st.session_state.something) not in df["Employee Code"].values:
            st.error("Wrong Code! Renter your Code")

        else:
            placeholder1, placeholder2, placeholder3, placeholder4 = st.empty(), st.empty(), st.empty(), st.empty()
            st.session_state.name = df[df["Employee Code"] == int( st.session_state.something)]["Employee Name"].values[0]
            Project = df[df["Employee Code"] == int( st.session_state.something)]["Project"].values[0]
            placeholder1.subheader("**Please Check and confirm your data!**")
            d = {'Name': [st.session_state.name ], 'Code': [ st.session_state.something], 'Project': [Project]}
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
                    except:
                        st.write("Loading.................")
                    # show_pages([Page("Login_Page.py", "Login Page"), Page("Pages\main.py", "Survey")])
                    # switch_page("Survey")
                    store = st.text_input("****Enter store name****")

                    if st.button("Submit"):
                        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                    #     # Write
                    #create this on secrects / TOML
                    ## google_service_account = {"type" = "service_account", "project_id", AND_SO_ON}
                        google_service_account= { "type": "service_account", "project_id": "big-depth-391213", "private_key_id": "1d14ac1a96de7f2f9ef144a7a691101064f735a6", "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC+YO9Pvm82CjEE\nKLe9xbfArNtq2bAJ3fAV17nkUaWW/TNOHe0pV+/4Yo/EN2FtMc2ciUeUg39zN8gz\nGQMZyD0HTayVHd6aJGMbj1XMbpxty3SoTAFQrAXQjVP0e1+y9NxJ6KvJnsOQdGrO\n2n7gqTEHC8oZBMtXTn66uecw5jKJg7PDiIX4mYPy0Q4p/N2lJKQuO45983C5tcmM\n/XMJzG8sR54bArItggB/q/8WBOCxXuMC6Pl64IJvHekhwfoaveOATD6f82IBWWB7\njJdDaQCF67MvpcyGEP+mkYRHcQqsw+Q2/MEbfYvJAL3GaY8qwWAY+mp3JZlrAhWg\nhkjkrf1rAgMBAAECggEAPP4oXZeI4LrWJlt3Noz0SH341BxHGnoo046oRz5jO2MG\nf2X2F/NM9fp5zebiR04X7ilLLgkNGZhLAxfl1upApyja/HEz4pV6zRcYaWUcp85x\nowOqvjJGsKC+v4qRR+/L7b/l3bQIOq0ZlQkKciayhuvfhTF0hhWnY2Jw78kocsaY\nvlnnENOx6gsefRwT2d+irOVZ0eL6Wtq9aBsP28s/Nbs8uIN8y3gldreJPU/nQ+68\nFoNx5ggjpjMpLPP7Hw3egWZCFvF+01Qjm9NBQ/I6UP2UZqbWzDY2rMTh23C/c/HC\npTyAzH2x8OwYTkLMcihdAQ0pwpSoVETljolbjeUO7QKBgQD+UxK2xQcKZIfpW7Xj\nQCBsO55vAF2Gxxc5g7fecNJhambJh+R92rm9cvh6Btt/zddJJDznbzxq6HPjMwLh\nJAa5SHPsseGY2A+G3g4z30yDK8kz3/wYBh9ZX/jETA/+d+a80kGtftA8NhQqn5AY\n+MJGP5gRqTjmTETuhMU//W4JtQKBgQC/ogPN6Y96hz5/036uGC+AWLBqPvxSZyqa\nRIJtd6vxQGNrN1YacG9nWr7Y3cSeXxtbECxfkmLSvOSErB5c3pYtZzjMq2M6fJge\n4ZvbPz9QeZMMNHoOr+i8+OriGtcwM9lsADIUxscd+r4t9jfnADwu97YDoXKFCIV4\nwaDI1B/enwKBgQDxykMZdppp/AfnCWUUp6vrmobXG27Pq0peSOcvWO365bDRWxwV\ntzQtdDfds9VNXYKXLBenJG85aMR8tcvABoNJ9iMYXkmQCaJBY633DQ3uC1vfsMw4\nfuGhFAgrf/EYyh+ZVwBQFSeehv+HQmo6A46YQO+vosXQ1aQXbC0n2CacnQKBgELL\nOt47yXngyAUP97jAz1XCFAOEXrhuIyhQNtHnA3R8h+qoCAgBJqN0us6mRdEZv1Q3\nR/Ar+uwPUOt5fr/KCbhboS2dk2Ggaflhk8yQuAXZykpXxC94Wvv7GwuiZVz0xZTi\nYJJjUqX9bupgRs3qhA+u4a9UR7Fc7gDQJLW7UjxrAoGAOP5DIw3fIG4woKp318Xi\n3ljraM6i2cdMwcYJePiKwkdxUBux8dV0Y/EXbJd3K0wOrsLKLrV+2VNJatXCWo0m\niye0Z+/aPNcUvJG9pS6Q7+utJ3HM4IimBkTKzwoaUDTxJ05o7plaisgzS/fwPI6B\n1oH/LD4ra/5pwubDHLzVRH8=\n-----END PRIVATE KEY-----\n", "client_email": "test-gs@big-depth-391213.iam.gserviceaccount.com","client_id": "101170581427661035112","auth_uri": "https://accounts.google.com/o/oauth2/auth","token_uri": "https://oauth2.googleapis.com/token","auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test-gs%40big-depth-391213.iam.gserviceaccount.com","universe_domain": "googleapis.com"}
                    # google_service_account_info = st.secrets['google_service_account']
                    # creds = ServiceAccountCredentials.from_json_keyfile_dict(google_service_account_info, scope)
                        creds = ServiceAccountCredentials.from_json_keyfile_dict(google_service_account, scope)

                    #     creds = ServiceAccountCredentials.from_json_keyfile_name('gapi.json', scope)
                        client = gspread.authorize(creds)
                        sh = client.open('Employee Data').worksheet('Sheet2')
                        row = [code, st.session_state.name,Project,st.session_state.date,str(location),str(utc),str(Now),str(timediff),store]
                        sh.append_row(row)
            elif nonConfirm:
                st.session_state.something = ""
                st._rerun()
                st.write("Please Re-enter your code")
