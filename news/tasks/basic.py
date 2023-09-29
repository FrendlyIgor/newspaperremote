from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def get_subscribers(category):
    user_email =[]
    for user in category.subscribers.all():
        user_email.append(user.email)
    return user_email

def new_post_subscriptions(instance):
    template = 'mail/new_post.html'

    for category in instance.category.all():
        email_subject = f'Новая публикация в категории "{category}"'
        user_emails = get_subscribers(category)
        html = render_to_string(
            template_name=template,
            context={
                'category': category,
                'post': instance,
            },
        )
        msg = EmailMultiAlternatives(
            subject=email_subject,
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=user_emails,
        )
        msg.attach_alternative(html, 'text/html')
        msg.send()
