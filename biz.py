import streamlit as st
from streamlit_option_menu import option_menu
import psycopg2
import pandas as pd 
import easyocr as ocr  
from PIL import Image 
import numpy as np
import cv2  
import re
import traceback

#---------------------------------------------------------------------------------------------------
def process_image(input_image,result):
    img_np = np.array(input_image)
    font = cv2.FONT_HERSHEY_SIMPLEX
    detected_texts = []

    # Process OCR results and draw bounding boxes
    for detection in result: 
        text = detection[1]
        detected_texts.append(text)

        # Draw bounding box
        top_left = tuple(map(int, detection[0][0]))
        bottom_right = tuple(map(int, detection[0][2]))
        if len(top_left) == 2 and len(bottom_right) == 2:
            img_np = cv2.rectangle(img_np, top_left, bottom_right, (0, 255, 0), 2)
        else:
            print("Invalid coordinates format")

        # Draw text
        text_position = (top_left[0], top_left[1] - 10)
        img_np = cv2.putText(img_np, text, text_position, font, 0.5, (255, 0, 0), 2, cv2.LINE_AA)
    
    return img_np, detected_texts
#-----------------------------------------------------------------------------------------------
def rex1(detected_texts):    
    bizdata = {
        "NAME" : [],
        "DESIGNATION" : [],
        "COMPANY" : [],
        "EMAIL" : [],
        "WEBSITE" : [],
        "ADDRESS" : [],
        "CONTACT" : []
    }
    bizdata["NAME"].append(detected_texts[0])
    bizdata["DESIGNATION"].append(detected_texts[1])

    for i in range(2,len(detected_texts)):
        if (detected_texts[i].replace("-","").isdigit()):
            bizdata["CONTACT"].append(detected_texts[i])

        elif "@" in detected_texts[i] and ".com" in detected_texts[i]:
            small =detected_texts[i].lower()
            bizdata["EMAIL"].append(small)

        elif "WWW" in detected_texts[i] or "www" in detected_texts[i] or "Www" in detected_texts[i] or "wWw" in detected_texts[i] or "wwW" in detected_texts[i]:
            small = detected_texts[i].lower()
            bizdata["WEBSITE"].append(small)

        elif re.match(r'^[A-Za-z]',detected_texts[i]):
            bizdata["COMPANY"].append(detected_texts[i])

        else:
            remove_colon = re.sub(r'[,;]', '', detected_texts[i])
            bizdata["ADDRESS"].append(remove_colon)

    for key,value in bizdata.items():
        if len(value)>0:
            concadenate = ' '.join(value)
            bizdata[key] = [concadenate]
        else:
            value = 'NA'
            bizdata[key] = [value]

    return bizdata
#---------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
#STREAMLIT

st.set_page_config(page_title="BizCardX", 
                   layout="wide")

st.markdown("<h1 style='font-size: 50px; text-align: Center;'>BizCardX ft. Optical Character Recognition</h1>", unsafe_allow_html=True)

SELECT = option_menu(
    menu_title = None,
    options = ["ABOUT","OCR READING","VIEW & MODIFY"],
    orientation="horizontal",
    icons=("book","laptop","puzzle"),
    styles=("font-size"== "15px",
        "text-align"== "center")
    )

if SELECT == "ABOUT":
    col1, col2 = st.columns(2)

    with col2:
        st.image("front.png", width=500)
    with col1:    
        st.markdown('<div style="text-align: justify;">BizCard OCR is a comprehensive Python application engineered to streamline the handling of business card data. Alongside its core functionality of extracting text from business card images using OCR technology, it boasts robust integration with databases, offering users extensive control over their data. This includes the ability to not only store extracted details but also to update and delete any unnecessary information as required. By providing such flexibility, BizCard OCR empowers users to maintain accurate and up-to-date contact databases effortlessly. This feature-rich application facilitates a smooth transition from traditional business cards to a digital format, revolutionizing contact management and bolstering productivity in networking and business endeavors.</div>', unsafe_allow_html=True)
                


if SELECT=="OCR READING":
    def load_model(): 
        reader = ocr.Reader(['en'])
        return reader 

    reader = load_model()
    
    image = st.file_uploader(label="Upload your BizCard here", type=['png', 'jpg', 'jpeg'])

    if image is not None:
        input_image = Image.open(image) 
        col1, col2 = st.columns(2)
        with col1:
            st.image(input_image)
     

    

        if st.button("Extract & Store Data",use_container_width= True):
            with st.spinner("🤖 Extracting Data... "):
                image_arr= np.array(input_image)
                result = reader.readtext(image_arr)
            img_np, detected_texts=process_image(input_image,result)
            bizdata=rex1(detected_texts)
            df= pd.DataFrame(bizdata)

            with col2:
                st.image(img_np, caption='Processed Image', use_column_width=True)
            st.success("Here you go!")
            st.balloons()
            
            st.write(df)

           
            try:
                # Establish database connection
                mydb = psycopg2.connect(
                    host='localhost',
                    user='postgres',
                    password='12345',
                    database='bizcard_database',
                    port=5432
                )
                cursor = mydb.cursor()

                # Check if the table exists and create it if necessary
                cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'bizcard')")
                table_exists = cursor.fetchone()[0]
                if not table_exists:
                    create_query = '''CREATE TABLE bizcard (
                                            NAME varchar(200),
                                            DESIGNATION varchar(150),
                                            COMPANY varchar(300),
                                            EMAIL varchar(100),
                                            WEBSITE varchar(100),
                                            ADDRESS text,
                                            CONTACT bigint
                                        )'''
                    cursor.execute(create_query)
                    mydb.commit()

                # Insert data into the table
                for index, row in df.iterrows():
                    insert_query = '''INSERT INTO bizcard (
                                            NAME, DESIGNATION, COMPANY, EMAIL, WEBSITE, ADDRESS, CONTACT
                                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)'''
                    values = (
                        row['NAME'],
                        row['DESIGNATION'],
                        row['COMPANY'],
                        row['EMAIL'],
                        row['WEBSITE'],
                        row['ADDRESS'],
                        row['CONTACT']
                    )
                    cursor.execute(insert_query, values)
                    mydb.commit()

                print("Data stored in database successfully!")
            except Exception as e:
                # Log the exception traceback
                traceback.print_exc()
                print(f"Error storing data: {e}")

if SELECT == "VIEW & MODIFY":
    if st.checkbox("View Saved Data"):
        mydb = psycopg2.connect(
                    host='localhost',
                    user='postgres',
                    password='12345',
                    database='bizcard_database',
                    port=5432
                )
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM bizcard")
        bizcard_data = cursor.fetchall()
        mydb.commit()

        df3= pd.DataFrame(bizcard_data, 
                          columns= ["NAME","DESIGNATION","COMPANY","EMAIL","WEBSITE","ADDRESS","CONTACT"])

        st.dataframe(df3)
        col1,col2,col3= st.columns(3)
        with col2:
            select_name = st.selectbox("Select the Name",df3["NAME"])
        
        df4 = df3[df3["NAME"]==select_name]
        st.write("")

        col1,col2= st.columns(2)
        with col1:
            modify_name= st.text_input("NAME", df4["NAME"].unique()[0])
            modify_desig= st.text_input("DESIGNATION", df4["DESIGNATION"].unique()[0])
            modify_company= st.text_input("COMPANY", df4["COMPANY"].unique()[0])
            modify_email= st.text_input("EMAIL", df4["EMAIL"].unique()[0])
            modify_web= st.text_input("WEBSITE", df4["WEBSITE"].unique()[0])
            modify_address= st.text_input("ADDRESS", df4["ADDRESS"].unique()[0])
            modify_contact= st.text_input("CONTACT", df4["CONTACT"].unique()[0])

            df4["NAME"] = modify_name
            df4["DESIGNATION"] = modify_desig
            df4["COMPANY"] = modify_company
            df4["EMAIL"] = modify_email
            df4["WEBSITE"] = modify_web
            df4["ADDRESS"] = modify_address
            df4["CONTACT"] = modify_contact

        
        col1,col2,col3= st.columns(3)
        with col1:
            button1= st.button("Modify")
        with col3:
            button2=st.button("Delete the entry")


        if button1:
            mydb = psycopg2.connect(
                    host='localhost',
                    user='postgres',
                    password='12345',
                    database='bizcard_database',
                    port=5432
                )
            cursor = mydb.cursor()
            cursor.execute(f"DELETE FROM bizcard WHERE NAME ='{select_name}'")
            mydb.commit()
            for index, row in df4.iterrows():
                insert_query = '''
                        INSERT INTO bizcard (NAME,DESIGNATION,COMPANY,
                                            EMAIL,WEBSITE,ADDRESS,CONTACT)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                '''
                values= (row['NAME'], row['DESIGNATION'], row['COMPANY'],
                        row['EMAIL'], row['WEBSITE'], row['ADDRESS'], row['CONTACT'])

                
            cursor.execute(insert_query,values)
            mydb.commit()
            st.success("Updated the modifications..")
            st.balloons()


        if button2:
            mydb = psycopg2.connect(
                    host='localhost',
                    user='postgres',
                    password='12345',
                    database='bizcard_database',
                    port=5432
                )
            cursor = mydb.cursor()
            cursor.execute(f"DELETE FROM bizcard WHERE NAME ='{select_name}'")
            mydb.commit()
            st.success("Deleted the entry from the database!")

        

            
        