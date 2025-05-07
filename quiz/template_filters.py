from django.template.defaulttags import register

@register.filter(name="get_item")
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name="num_correct")
def num_correct(objects):
    return sum(1 for result in objects if result.is_correct)

@register.filter(name="make_percentage")
def make_percentage(correct, total):
    return (correct / total) * 100