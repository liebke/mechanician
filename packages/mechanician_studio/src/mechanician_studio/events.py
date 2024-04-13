from abc import ABC, abstractmethod
import asyncio
from aioprocessing import AioQueue
from fastapi import FastAPI
import logging


class EventHandler(ABC):
    @abstractmethod
    async def handle(self, event):
        """
        Asynchronously handle an event represented as a dictionary.
        """
        pass


class EventProcessor:
    def __init__(self):
        self.handlers = {}  # Maps event types to lists of handlers
        self.queue = AioQueue()
        self.running = False
        self.task = None

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
            await handler.handle(event)
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

# Application setup
# app = FastAPI()
# processor = EventProcessor()

# @app.on_event("startup")
# async def startup_event():
#     # Register handlers
#     # Example: processor.register_handler('info', InfoEventHandler())
#     # Example: processor.register_handler('error', ErrorEventHandler())
#     await processor.start()

# @app.on_event("shutdown")
# async def shutdown_event():
#     await processor.stop()

# @app.post("/events/")
# async def create_event(event: dict):
#     await processor.add_event(event)
#     return {"message": "Event added successfully"}


###############################################################################
# Example usage
###############################################################################
            

# class InfoEventHandler(EventHandler):
#     async def handle(self, event):
#         print(f"INFO: {event['message']}")


# class InfoEventHandler2(EventHandler):
#     async def handle(self, event):
#         print(f"INFO 2: {event['message']}")

# class ErrorEventHandler(EventHandler):
#     async def handle(self, event):
#         print(f"ERROR: {event['message']}")



# async def main():
#     processor = EventProcessor()
#     processor.register_handler('info', InfoEventHandler())
#     processor.register_handler('info', InfoEventHandler2())
#     processor.register_handler('error', ErrorEventHandler())
#     supervisor_task = asyncio.create_task(processor)

#     # Add some events to the processor
#     await processor.add_event({'type': 'info', 'message': 'System boot successful.'})
#     await processor.add_event({'type': 'error', 'message': 'Failed to connect to database.'})

#     # Simulate running and then stopping
#     await asyncio.sleep(5)
#     await processor.stop()  # Now properly awaiting stop
#     await asyncio.sleep(1)  # Give time for shutdown process

# asyncio.run(main())
