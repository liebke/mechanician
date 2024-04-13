from abc import ABC, abstractmethod
import asyncio
from aioprocessing import AioQueue
import logging


class EventHandler(ABC):
    @abstractmethod
    async def handle(self, context, event):
        """
        Asynchronously handle an event represented as a dictionary.
        """
        pass


class EventProcessor:
    
    def __init__(self, context):
        self.handlers = {}  # Maps event types to lists of handlers
        self.queue = AioQueue()
        self.running = False
        self.task = None
        self.context = context


    def register_handler(self, event_type, handler):
        """Register a handler for a specific type of event."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)


    async def add_event(self, event):
        """Add an event to the queue for processing."""
        await self.queue.coro_put(event)


    async def run(self):
        """Continuously process events until a shutdown signal is received."""
        self.running = True
        while self.running:
            event = await self.queue.coro_get()
            if event is None:  # Shutdown signal
                break
            event_type = event.get('type')
            if event_type in self.handlers:
                tasks = [self.handle_event(handler, event) for handler in self.handlers[event_type]]
                await asyncio.gather(*tasks)


    async def handle_event(self, handler, event):
        """Handle events with proper error catching for each handler."""
        try:
            await handler.handle(self.context, event)
        except Exception as e:
            logging.error(f"Error handling event {event} with handler {handler}: {e}")


    async def start(self):
        """Start the event processor asynchronously."""
        if not self.running:
            self.task = asyncio.create_task(self.run())


    async def stop(self):
        """Stop processing events and shutdown cleanly."""
        self.running = False
        await self.queue.coro_put(None)  # Send a shutdown signal to the event loop
        if self.task:
            await self.task  # Ensure the run task completes
