from django import template
import json

register = template.Library()

@register.filter(name='list_first')
def image_data(object):
    file_list = json.loads(object)
    if file_list:
        file_path=file_list[0]
    else:
        file_path = "empty list"
    #print(file_path)
    return file_path