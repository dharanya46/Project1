import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",    
        password="12345678",
        database="project_redbus"      
    )

def get_distinct_States():
    conn = get_connection()
    query = "SELECT DISTINCT States FROM bus_routes"
    cursor = conn.cursor()
    cursor.execute(query)
    state = [row[0] for row in cursor.fetchall()]
    conn.close()
    return state

def get_distinct_route_names(state=None):
    conn = get_connection()
    query = "SELECT DISTINCT route_name FROM bus_routes"
    if state:
        query += " WHERE States = %s"
    cursor = conn.cursor()
    cursor.execute(query, (state,) if state else None)
    routes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return routes

def get_distinct_bustype(routes=None):
    conn = get_connection()
    query = "SELECT DISTINCT bustype FROM bus_routes"
    if routes:
        query += " WHERE route_name = %s"
    cursor = conn.cursor()
    cursor.execute(query, (routes,) if routes else None)
    buses = [row[0] for row in cursor.fetchall()]
    conn.close()
    return buses



def query_buses(States=None, route_name=None, price=None, bustype=None, departing_time=None, star_rating=None):
    conn = get_connection()
    query = "SELECT route_name, price, bustype, departing_time, duration, reaching_time, star_rating, price, seats_available FROM bus_routes WHERE 1=1"
    #query = "SELECT route_name, price, bustype, TIME_FORMAT(departing_time,'%H:%i:%s'), star_rating FROM bus_routes"  
    params = []

    if States:
        query += " AND States = %s"
        params.append(States)

    if route_name:
        query += " AND route_name  = %s"
        params.append(route_name)
    if price is not None:
        query += " AND price >= %s"
        params.append(price)
    if bustype:
        query += " AND bustype = %s"
        params.append(bustype)
    if departing_time is not None:
        query += " AND TIME(departing_time) >= %s"
        params.append(departing_time)
    if star_rating is not None:
        query += " AND star_rating >= %s"
        params.append(star_rating)

    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    m = pd.DataFrame(data)
    #print(m)
    m['reaching_time'] = m['reaching_time'].astype(str)
    m['departing_time'] = m['departing_time'].astype(str)
    #m['reaching_time'] = m['reaching_time'].replace('0 days' ,'')
    #m['reaching_time'] = m['reaching_time'].apply(lambda x: datetime.strftime(x, format="%Y-%m-%d"))
    #m['reaching_time'] = m['reaching_time'].astype(str)
    #st.table(m)
    #st.write(m)
    return m



st.title("Choose Bus as You Wish")



r = st.sidebar.radio('Navigation',['Home','Choose Bus'])
if r =='Home':
    st.image("D:\Guvi_project\TSR Watermark - 8033.jpg")
    name = st.text_input('Enter your name: ')
    st.write(f"WELCOME {name}")
    st.write('Choose your bus by clicking the option "Choose Bus"')
if r == 'Choose Bus':

    state_name = get_distinct_States()

    state_filter = st.selectbox("Select State", options=["All"] + state_name)
    
    #route_names = get_distinct_route_names()
    route_names = get_distinct_route_names(state_filter if state_filter != "All" else None)
   
    route_filter = st.selectbox("Select Route", options=["All"]+route_names)

    
    price_filter = st.slider("Price", min_value=0, max_value=700, value=0)


    bustypes = get_distinct_bustype(route_filter if route_filter != "All" else None)

    
    bustype_filter = st.selectbox("Select bustype", options=["All"] + bustypes)
    

   
    departing_time_filter = st.time_input("select a time")
  
    star_rating_filter = st.slider("Star Rating", min_value=0, max_value=5, value=0)

    if st.button("Search"):
        state_filter_value = None if state_filter == "All" else state_filter
        route_filter_value = None if route_filter == "All" else route_filter
        bustype_filter_value = None if bustype_filter == "All" else bustype_filter

        data = query_buses(
            States=state_filter_value,
            route_name=route_filter_value, 
            price=price_filter, 
            bustype=bustype_filter_value, 
            departing_time=departing_time_filter if departing_time_filter else None,
            star_rating=star_rating_filter if star_rating_filter is not None else None
        )
        if data.empty:
            st.write("No buses found.")
        else:
            st.dataframe(data)
  
