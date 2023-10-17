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

selected = option_menu(menu_title=None,options=["Employee","Company"],icons=["person-vcard-fill","building"],orientation="horizontal")

if selected == "Employee":
    time = dt.now()
    time_format = "%Y-%m-%d  %H:%M:%S.%f"
    date = str(time.date())
    timestamp = str(time.time())
    utc = dt.utcnow().replace(tzinfo=pytz.UTC)
    # utc = str(datetime.datetime.now(datetime.timezone.utc))
    t = utc + datetime.timedelta(hours=3)

    timezone = pytz.timezone("Africa/Cairo")
    aware1 = timezone.localize(time)
    OFFSET = aware1.utcoffset()

    nonConfirm = False

    col1, col2 = st.columns([1,3])
    with col1:
        st.image("Smart FieldLogo.jpg")
    with col2:
        st.title("    Smart Field Application")
    text = st.empty()
    code = text.text_input("****Enter your code****",max_chars=4,key="1")
    if code!= "":
        # Create a connection object.
        conn = st.experimental_connection("gsheets", type=GSheetsConnection)

        df = conn.read(worksheet="Sheet1",
                       ttl="10s",
                       usecols=[0, 1, 2],
                       nrows=5)
        if int(code) not in df["Employee Code"].values:
            st.error("Wrong Code!")
            ti.sleep(1)
            #pyautogui.hotkey("ctrl", "F5")
        else:
            placeholder1, placeholder2, placeholder3,placeholder4 = st.empty(), st.empty(), st.empty(), st.empty()
            name = df[df["Employee Code"]==int(code)]["Employee Name"].values[0]
            Project = df[df["Employee Code"] == int(code)]["Project"].values[0]
            placeholder1.subheader("**Hello {}, Please Check and confirm your data.**".format(name))
            d = {'Name': [name], 'Code': [code],'Project': [Project] }
            emp_df = pd.DataFrame(data=d,index=[""])
            Employee_data = placeholder2.table(emp_df[0:])


            col5, col6 = st.columns([1, 1])
            with col5:
                Confirm = placeholder3.checkbox("Confirmed ✔")

            with col6:
                nonConfirm = placeholder4.checkbox("Not Confirmed ❌")

            if Confirm:
                placeholder3.empty()
                placeholder4.empty()
                if st.checkbox("Check my location"):
                   try:
                        user_agent = 'user_me_{}'.format(randint(10000, 99999))
                        geolocator = Nominatim(user_agent = 'MYAPP')
                        loc = get_geolocation()
                        ti.sleep(2.5)
                        latitude = loc['coords']['latitude']
                        longitude = loc['coords']['longitude']
                        actual_coordinates = "{},{}".format(latitude, longitude)
                        location = geolocator.reverse(actual_coordinates)
                        address = location.raw['address']
                        # Target_Location = employees[employee_code][2]
                        # Distance = round(geopy.distance.geodesic(Target_Location, actual_coordinates).km, 2)
                        st.write(actual_coordinates," \n ", location)
                   except:
                        st.write("Loading.................")

                   if st.button("Submit"):
                        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                        # Write
                        creds = ServiceAccountCredentials.from_json_keyfile_name('gapi.json', scope)
                        client = gspread.authorize(creds)
                        sh = client.open('Employee Data').worksheet('Sheet2')
                        row = [code, name,Project,date,timestamp,str(location),str(utc),str(t),str(OFFSET)]
                        sh.append_row(row)
            #elif nonConfirm:
                #pyautogui.hotkey("ctrl", "F5")

elif selected == "Company":
    text1,text2 = st.empty(),st.empty()
    Companynameoriginal = "IFM"
    Passwordoriginal =    "1234"

    Companyname = text1.text_input("****Company Name****", max_chars=20, key="3")
    Password = text2.text_input("****Password****", max_chars=20, key="4")

    if Companyname == Companynameoriginal and Password==Passwordoriginal:
        text1.empty()
        text2.empty()
        st.success("Login Success")
        DATE = st.date_input("Choose a day")
        conn = st.experimental_connection("gsheets", type=GSheetsConnection)

        allemp = conn.read(worksheet="Sheet1",
                       ttl="10s",
                       usecols=[0, 1, 2],
                       nrows=10000).dropna(subset=['Employee Code'])

        Attendance = conn.read(worksheet="Sheet2",
                           ttl="10s",
                           usecols=[0, 1, 2,3,4,5,6,7,8],
                           nrows=10000).dropna(subset=['Employee Code'])
        #st.write(Attendance.merge(allemp, on = ["Employee Code","Employee Name","Project"],how="right"))

        datebaesddf = Attendance[Attendance["Date"]==str(DATE)]
        allemp["Attenance Status"] =["Attend" if x in datebaesddf["Employee Code"].values else "Absent" for x in allemp["Employee Code"]]
        allemp = datebaesddf.merge(allemp,on = ["Employee Code","Employee Name","Project"],how="right")
        st.write(allemp)
        st.download_button("Dowmload Attendance status",data=allemp.to_csv(),file_name='large_df.csv', mime='text/csv')
    # else:
    #     st.error("Wrong data!")
    #     pyautogui.hotkey("ctrl", "F5")

# latitude = loc['coords']['latitude']
# longitude = loc['coords']['longitude']
# actual_coordinates = "{},{}".format(latitude, longitude)
# location = geolocator.reverse(actual_coordinates)
# address = location.raw['address']
# # Target_Location = employees[employee_code][2]
# # Distance = round(geopy.distance.geodesic(Target_Location, actual_coordinates).km, 2)
# # st.write("**Your Coordinates are:**", actual_coordinates, "  \n **Address**: ", location)
# # st.write("You are ", "**{}**".format(str(Distance)), " Km From your target location")

