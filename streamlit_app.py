import streamlit
import pandas
import requests
import snowflake.connector
from urllib.error import URLError


streamlit.title("My Parents New Healthy Diner")
streamlit.header('Breakfast Menu')
streamlit.text('🥣 Omega 3 & Blueberry Oatmeal')
streamlit.text('🥗 Kale, Spinach & Rocket Smoothie')
streamlit.text('🐔Hard-Boiled Free-Range Egg')
streamlit.text('🥑🍞 Avacado Toast')

streamlit.header('🍌🥭 Build Your Own Fruit Smoothie 🥝🍇')

my_fruit_list= pandas.read_csv("https://uni-lab-files.s3.us-west-2.amazonaws.com/dabw/fruit_macros.txt")
my_fruit_list=my_fruit_list.set_index('Fruit')
fruits_selected=streamlit.multiselect("Pick some fruits:", list(my_fruit_list.index),['Avocado','Strawberries'])

#streamlit.dataframe(my_fruit_list)

fruits_to_show = my_fruit_list.loc[fruits_selected]
streamlit.dataframe(fruits_to_show)

streamlit.header("Fruityvice Fruit Advice!")

def get_fruityvice_data(fruit_choice):
  """
  Go get them fruity sample data.
  """
  fruityvice_response = requests.get("https://fruityvice.com/api/fruit/"+fruit_choice)
  # read it from json
  fruityvice_normalized = pandas.json_normalize(fruityvice_response.json())
  return fruityvice_normalized

try:
#streamlit.text(fruityvice_response.json())
  fruit_choice = streamlit.text_input('What fruit would you like information about?')
  if not fruit_choice:
    streamlit.error("Please select a fruit to get information")
  else:
    #streamlit.write('The user entered ', fruit_choice)
    fruityvice_normalized = get_fruityvice_data(fruit_choice)
    # put it out as a table
    streamlit.dataframe(fruityvice_normalized)
except URLError as e:
  streamlit.error()
  
streamlit.header("The fruit load list contains:")
#special snowflake
def get_fruit_load_list(my_cnx):
  with my_cnx.cursor() as my_cur:
    my_cur.execute("select * from fruit_load_list")
    return my_cur.fetchall()
  
if streamlit.button("Get Fruit Load List"):
  my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
  my_data_rows =  get_fruit_load_list(my_cnx) 
  my_cnx.close()
  streamlit.dataframe(my_data_rows)

def insert_row_snowflake(new_fruit,my_cnx):
  with my_cnx.cursor() as my_cur:
    my_cur.execute("insert into fruit_load_list values ('"+new_fruit+"')")
    return "Thanks for adding "+new_fruit

add_my_fruit= streamlit.text_input("What fruit would you like to add?")
if streamlit.button('Add a fruit to the list'):
  my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
  result = insert_row_snowflake(add_my_fruit,my_cnx)
  my_cnx.close()
  streamlit.text(result)
streamlit.stop()

