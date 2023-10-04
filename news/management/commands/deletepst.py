from django.core.management.base import BaseCommand, CommandError
from news.models import Post


class Command(BaseCommand):
    help = "Удаляет все новости из какой-либо категории, но только при подтверждении действия в консоли при выполнении команды"
    requires_migrations_checks = True

    def handle(self, *arg, **options):
        self.stdout.readable()
        self.stdout.write('Вы действительнор хотите удалить все посты? yes/no')
        answer =  input()

        if answer == 'yes': # в случае подтверждения действительно удаляем все товары
            Post.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Посты успешно удалены!'))
            return
 
        self.stdout.write(self.style.ERROR('Отказано')) # в случае неправильного подтверждения, говорим, что в доступе отказано