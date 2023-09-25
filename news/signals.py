from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from news.models import PostCategory
from news.tasks.basic import new_post_subscriptions


@receiver(m2m_changed, sender=PostCategory)#чтобы функция отработала по сигналу используется декоратор
def notify_subscribers(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':# обращаемся к словарю с ключами kwargs, сработало ли действие post_add
        pass
        new_post_subscriptions(instance)