import os
def get_save_location(terms):
    save_location = os.path.join(
        r'images', '_'.join(x.capitalize() for x in terms), r'{}.{}'
    )

    if not os.path.isdir(os.path.dirname(save_location)):
        os.makedirs(os.path.dirname(save_location))
    return save_location

def check_if_result_b64(source):
    possible_header = source.split(',')[0]
    if possible_header.startswith('data') and ';base64' in possible_header:
        image_type = possible_header.replace('data:image/', '').replace(';base64', '')
        return image_type
    return False