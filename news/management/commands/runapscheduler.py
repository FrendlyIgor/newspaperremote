import logging
 
from django.conf import settings
 
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.core.mail import send_mail, EmailMultiAlternatives
from ...models import Category, Post 
from django.utils import timezone
from django.urls import reverse
from datetime import datetime, timedelta
from django.template.loader import render_to_string
 
logger = logging.getLogger(__name__)
 
 
# наша задача по выводу текста на экран
def send_weekly_posts_list():
    start_date = datetime.today() - timedelta(days=6)
    this_weeks_posts = Post.objects.filter(dataCategory__gt=start_date)
    for cat in Category.objects.all():
        post_list = this_weeks_posts.filter(category=cat)
        if post_list:
            subscribers = cat.subscribers.all()
            context = {
                'post_list': post_list,
                'cat': cat,
            }

            for sub in subscribers:
                context['sub'] = sub
                html_content = render_to_string('weekly_posts_list.html', context)

                msg = EmailMultiAlternatives(
                    subject=f'{cat.CategoryName}: Посты за прошедшую неделю',
                    from_email='divIgordiv@yandex.ru',
                    to=[sub.email],
                )
                msg.attach_alternative(html_content, "text/html")
                """ msg.send() """
                print(html_content)
 
 
# функция которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)
 
 
class Command(BaseCommand):
    help = "Runs apscheduler."
 
    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")
        
        # добавляем работу нашему задачнику
        scheduler.add_job(
            send_weekly_posts_list,
            trigger=CronTrigger(second="*/10"),  # Тоже самое что и интервал, но задача тригера таким образом более понятна django
            id="send_weekly_posts_list",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(year="2500"),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'send_weekly_posts_list'.")

        
 
        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")