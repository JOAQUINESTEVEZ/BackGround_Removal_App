import streamlit as st 
from streamlit_image_coordinates import streamlit_image_coordinates as im_coordinates
from streamlit_dimensions import st_dimensions
from PIL import Image
import cv2
import os
import base64
import numpy as np
import requests
import io
from PIL import Image as PILImage

api_endpoint = "https://students-uwf.us-east-1.modelbit.com/v1/remove_background/latest"

# Set Layout
st.set_page_config(layout='wide')

def set_background(image_file):
    """
    This function sets the background of a Streamlit app to an image specified by the given image file.

    Parameters:
        image_file (str): The path to the image file to be used as the background.

    Returns:
        None
    """
    with open(image_file, "rb") as f:
        img_data = f.read()
    b64_encoded = base64.b64encode(img_data).decode()
    style = f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{b64_encoded});
            background-size: cover;
        }}
        </style>
    """
    st.markdown(style, unsafe_allow_html=True)


set_background('./bg.jpg')



col01, col02 = st.columns(2)

# Instructions content
info_content = """
1. Drop a file
2. Click on the part of the image you want to get
3. Remove background
"""
container_style = """
    background-color: #040f13;
    color: white;
    padding: 10px;
    border-radius: 5px;
"""

col02.markdown(
    f"""
    <div style="{container_style}">
        <b>Instructions:</b><br>
        {info_content}
    </div>
    """,
    unsafe_allow_html=True
)



# File Uploader
file = col02.file_uploader('', type=['jpeg', 'jpg', 'png'])

# Read Images
if file is not None:
    image = Image.open(file).convert('RGB')

    image = image.resize((685, int(image.height * 685 / image.width)))

    # Create Buttons
    col1, col2 = col02.columns(2)

    placeholder0 = col02.empty()
    with placeholder0:
        value = im_coordinates(image)
        if value is not None:
            print(value)

    if col1.button('Original', use_container_width=True):
        placeholder0.empty()
        placeholder1 = col02.empty()
        with placeholder1:
            col02.image(image, use_column_width=True)

    if col2.button('Remove Background', type='primary', use_container_width=True):
        placeholder0.empty()
        placeholder2 = col02.empty()

        filename = '{}_{}_{}.png'.format(file.name, value['x'], value['y'])
        if os.path.exists(filename):
            result_image = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
       
        else:
            _, image_bytes = cv2.imencode('.png', np.asanyarray(image))

            image_bytes = image_bytes.tobytes()

            image_bytes_encoded_base64 = base64.b64encode(image_bytes).decode('utf-8')

            api_data = {"data": [image_bytes_encoded_base64, value['x'], value['y']]}
            response = requests.post(api_endpoint, json=api_data)
            #print(response.json())

            result_image = response.json()['data']

            result_image_bytes = base64.b64decode(result_image)

            result_image = cv2.imdecode(np.frombuffer(result_image_bytes, dtype=np.uint8), cv2.IMREAD_UNCHANGED)

            cv2.imwrite(filename, result_image, [cv2.IMWRITE_PNG_COMPRESSION, 0])
          
        with placeholder2:
            result_image_pil = PILImage.fromarray(np.uint8(result_image))
            image_bytes = io.BytesIO()
            result_image_pil.save(image_bytes, format='PNG')
            final_img = st.image(result_image_pil, use_column_width=True)

            btn = st.download_button(
                    label="Download image",
                    data=image_bytes.getvalue(),
                    file_name="img.png",
                    mime="image/png/streamlit.delta_generator.DeltaGenerator"
                )
            
            col02.image(result_image, use_column_width=True)
