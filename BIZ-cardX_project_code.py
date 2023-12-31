import streamlit as st
import easyocr
import sqlite3
import numpy as np
from PIL import Image
import io

def create_table():
    conn = sqlite3.connect("business_cards.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS business_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image BLOB NOT NULL,
            company_name TEXT,
            card_holder_name TEXT,
            designation TEXT,
            mobile_number TEXT,
            email TEXT,
            website_url TEXT,
            area TEXT,
            city TEXT,
            state TEXT,
            pin_code TEXT
        )
    ''')

    conn.commit()
    conn.close()

# Initialize easyOCR reader
reader = easyocr.Reader(['en'])  # Language: English

def main():
    # Set the title and page layout
    st.title("Business Card OCR Application")
    st.markdown("Upload a business card image and extract its information using OCR.")

    # Create a sidebar for user actions
    st.sidebar.title("Database Actions")
    action = st.sidebar.radio("Select an Action", ["Add Data", "View Data", "Delete Data"])

    # Initialize the database
    create_table()


    if action == "Add Data":
        # Upload image and process it
        uploaded_file = st.file_uploader("Upload a business card image", type=["jpg", "png", "jpeg"])

        if uploaded_file is not None:
            # Display the uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Business Card", use_column_width=True)

            # Convert the image to a numpy array for easyOCR
            image_np = np.array(image)

            # Extract text from the image using easyOCR
            extracted_text = reader.readtext(image_np)

            # Display the extracted information
            st.header("Extracted Information:")
            for item in extracted_text:
                st.write(item[1])  # Display the text

            # Save data to database
            if st.button("Save Data"):
                conn = sqlite3.connect("business_cards.db")
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO business_cards (image, company_name, card_holder_name, designation, 
                                                mobile_number, email, website_url, area, city, state, pin_code)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (uploaded_file.read(), extracted_text[0][1], extracted_text[1][1], extracted_text[2][1],
                      extracted_text[3][1], extracted_text[4][1], extracted_text[5][1], extracted_text[6][1],
                      extracted_text[7][1], extracted_text[8][1], extracted_text[9][1]))

                conn.commit()
                conn.close()
                st.success("Data saved to database successfully!")

    elif action == "View Data":
        # View data from database
        conn = sqlite3.connect("business_cards.db")
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM business_cards''')
        data = cursor.fetchall()

        if len(data) == 0:
            st.warning("No data available in the database.")
        else:
            st.header("View Data:")
            st.table(data)

            st.write("---")

            # Allow user to update data
            selected_id = st.number_input("Enter the Business Card ID to update", min_value=1, step=1)
            if st.button("Update"):
                if selected_id in [row[0] for row in data]:
                    # Update the data in the table
                    company_name = st.text_input("Company Name", data[selected_id-1][2])
                    card_holder_name = st.text_input("Card Holder Name", data[selected_id-1][3])
                    designation = st.text_input("Designation", data[selected_id-1][4])
                    mobile_number = st.text_input("Mobile Number", data[selected_id-1][5])
                    email = st.text_input("Email", data[selected_id-1][6])
                    website_url = st.text_input("Website URL", data[selected_id-1][7])
                    area = st.text_input("Area", data[selected_id-1][8])
                    city = st.text_input("City", data[selected_id-1][9])
                    state = st.text_input("State", data[selected_id-1][10])
                    pin_code = st.text_input("Pin Code", data[selected_id-1][11])

                    update_query = "UPDATE business_cards SET company_name=?, card_holder_name=?, designation=?, mobile_number=?, email=?, website_url=?, area=?, city=?, state=?, pin_code=? WHERE id=?"
                    cursor.execute(update_query, (company_name, card_holder_name, designation, mobile_number, email, website_url, area, city, state, pin_code, selected_id))
                    conn.commit()
                    conn.close()
                    st.success("Data updated successfully!")
                else:
                    st.warning("No data found with the given ID.")

    elif action == "Delete Data":
        # Delete data from the database
        selected_id = st.number_input("Enter the Business Card ID to delete", min_value=1, step=1)
        if st.button("Delete"):
            conn = sqlite3.connect("business_cards.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM business_cards WHERE id=?", (selected_id,))
            conn.commit()
            conn.close()
            st.success("Data deleted successfully!")

            # Reset the selected ID to avoid accidental deletion
            selected_id = None

if __name__ == "__main__":
    main()
