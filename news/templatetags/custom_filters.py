from django import template

register = template.Library()

@register.filter(name = 'mult')
def mult(value, arg):
    return str(value)*arg




register = template.Library()


bad_word_list=(
    "mat1",
    "mat2",
    "mat3",
)
@register.filter(name='censor')

def censor(value):
    for word in bad_word_list:
        value = value.replace(word, '*' * len(word))
        return str(value)

        
