from dependency_injector import containers, providers

from core.rabbitmq import TaskPublisher

class Container(containers.DeclarativeContainer):
    """
    Контейнер для зависимостей приложения
    """

    wiring_config = containers.WiringConfiguration(packages=["api.v1"])

    # NOTE: Бэк хочет сюда перенести свои сервисы?
    publisher = providers.Singleton(TaskPublisher)