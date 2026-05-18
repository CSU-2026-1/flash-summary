from fastapi import Request
from core.rabbitmq import TaskPublisher

def get_publisher(request: Request) -> TaskPublisher:

    # NOTE: Возможно лучше переписать под контейнер как в демо проекте

    return request.app.state.publisher