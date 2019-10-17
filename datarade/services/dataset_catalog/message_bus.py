"""
This is the message bus for the Dataset Catalog service. It is politely borrowed almost whole cloth from the book
linked below. There are currently no events or commands hooked up to this bus, so it doesn't do anything at the
moment. However, this is expected to change in the near future, so it has been setup ahead of that point in time.

Original Source: https://github.com/python-leap/code/blob/master/src/allocation/messagebus.py
"""
import inspect
import traceback
from typing import Callable, Union, TYPE_CHECKING

from datarade.domain import events

if TYPE_CHECKING:
    from datarade.services.dataset_catalog import unit_of_work

Message = Union[events.Event]


class MessageBus:

    def __init__(self, uow: 'unit_of_work.AbstractUnitOfWork'):
        self.uow = uow
        self.dependencies = dict(uow=uow)

    def handle(self, message: Message):
        if isinstance(message, events.Event):
            self.handle_event(message)
        else:
            raise Exception(f'{message} was not an Event')

    def handle_event(self, event: events.Event):
        for handler in EVENT_HANDLERS[type(event)]:
            try:
                print('handling event', event, 'with handler', handler, flush=True)
                self.call_handler_with_dependencies(handler, event)
            except:
                print(f'Exception handling event {event}\n:{traceback.format_exc()}')
                continue

    def call_handler_with_dependencies(self, handler: Callable, message: Message):
        params = inspect.signature(handler).parameters
        deps = {name: dependency for name, dependency in self.dependencies.items() if name in params}
        handler(message, **deps)


EVENT_HANDLERS = {}
COMMAND_HANDLERS = {}
