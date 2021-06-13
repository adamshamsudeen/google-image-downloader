
import base64
import requests
from io import BytesIO
from PIL import Image
from PIL import UnidentifiedImageError

def check_if_result_b64(source):
    possible_header = source.split(',')[0]
    if possible_header.startswith('data') and ';base64' in possible_header:
        image_type = possible_header.replace('data:image/', '').replace(';base64', '')
        return image_type
    return False

def process(i ,attribute_value, save_location):
    try:

        # issue 1: if the image is base64, requests get won't work because the src is not an url
        is_b64 = check_if_result_b64(attribute_value)
        if is_b64:
            image_format = is_b64
            content = base64.b64decode(attribute_value.split(';base64')[1])
        else:
            
            resp = requests.get(attribute_value, stream=True)
            temp_for_image_extension = BytesIO(resp.content)
            
            image = Image.open(temp_for_image_extension)
            image_format = image.format
            content = resp.content
        # issue 2: if you 'open' a file, later you have to close it. Use a "with" pattern instead
        with open(save_location.format(i, image_format), 'wb') as f:
            f.write(content)
    except:
        pass