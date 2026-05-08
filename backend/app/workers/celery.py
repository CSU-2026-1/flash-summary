from celery import Celery

# TODO: Настройка
app = Celery("todo", broker="url")