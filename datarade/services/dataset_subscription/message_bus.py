"""
This is the message bus for the Dataset Subscription service. It is politely borrowed almost whole cloth from the book
linked below.

Original Source: https://github.com/python-leap/code/blob/master/src/allocation/messagebus.py
"""
import inspect
import traceback
from typing import Callable, Union, TYPE_CHECKING

from datarade.services.dataset_subscription import handlers
from datarade.domain import commands, events

if TYPE_CHECKING:
    from datarade.services.dataset_subscription import unit_of_work

Message = Union[commands.Command, events.Event]


class MessageBus:

    def __init__(self, uow: 'unit_of_work.AbstractUnitOfWork'):
        self.uow = uow
        self.dependencies = dict(uow=uow)

    def handle(self, message: Message):
        if isinstance(message, events.Event):
            self.handle_event(message)
        elif isinstance(message, commands.Command):
            self.handle_command(message)
        else:
            raise Exception(f'{m} was not an Event or Command')

    def handle_event(self, event: events.Event):
        for handler in EVENT_HANDLERS[type(event)]:
            try:
                print('handling event', event, 'with handler', handler, flush=True)
                self.call_handler_with_dependencies(handler, event)
            except:
                print(f'Exception handling event {event}\n:{traceback.format_exc()}')
                continue

    def handle_command(self, command: commands.Command):
        print('handling command', command, flush=True)
        try:
            handler = COMMAND_HANDLERS[type(command)]
            self.call_handler_with_dependencies(handler, command)
        except Exception as e:
            print(f'Exception handling command {command}: {e}')
            raise e

    def call_handler_with_dependencies(self, handler: Callable, message: Message):
        params = inspect.signature(handler).parameters
        deps = {name: dependency for name, dependency in self.dependencies.items() if name in params}
        handler(message, **deps)


EVENT_HANDLERS = {}
COMMAND_HANDLERS = {
    commands.CreateDatasetContainer: handlers.create_dataset_container,
    commands.CreateDataset: handlers.add_dataset,
    commands.RefreshDataset: handlers.refresh_dataset,
    commands.WriteDatasetFromDatabaseToDatabase: handlers.write_dataset_from_database_to_database,
}
