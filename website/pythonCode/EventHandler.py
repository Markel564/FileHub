from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class EventHandler:

    def __init__(self, path):
        self.path = path
        self.event_handler = FileSystemEventHandler()
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.path, recursive=True)

    def on_any_event(self, event):
        print ("Event: ", event)
        self.event.set()
    

    def start(self):
        self.event_handler.on_any_event = self.on_any_event
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()

        