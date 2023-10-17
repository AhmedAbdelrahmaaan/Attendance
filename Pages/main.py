import streamlit as st
from streamlit_extras.no_default_selectbox import selectbox

col1, col2 = st.columns([1, 7])
with col1:
    st.image("ifmlogo.jpg",width=100)
with col2:
    st.title("Intelligent For Field Marketing")









Date = st.date_input("Visit Date")
if Date == None or Date =="":
    st.error("تاريخ الزيارة اجباري")

Name = st.selectbox(label="Name",options=[st.session_state.name])
if Name == None or Name =="":
    st.error("الاسم اجباري")

Government = selectbox(label="المحافظة",options=["القاهرة","الجيزة"],no_selection_label="")
Area = st.text_input("المنطقة")
Address = st.text_input("العنوان بالتفصيل")


# XCOOR
# YCOOR
outletname = st.text_input("اسم المحل")
responsiblename = st.text_input("اسم المسؤول")
responsiblephone = st.text_input("رقم تليفون المسؤول")
outletsize = selectbox(label="حجم المحل", options =["كبير","متوسط","صغير"] ,no_selection_label="")
trader = selectbox(label="التاجر", options =["تجزئة","تاجر","جملة"] ,no_selection_label="")


st.write(Date,Name,Government)
