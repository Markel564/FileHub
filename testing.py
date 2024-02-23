import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

def on_created(event):
    print(f"{event.src_path} has been created!")

def on_deleted(event):
    print(f"Someone deleted {event.src_path}!")

def on_modified(event):
    print(f"{event.src_path} has been modified")

def on_moved(event):
    print(f"Moved {event.src_path} to {event.dest_path}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    event_handler = FileSystemEventHandler()

    # Assigning event handling functions
    event_handler.on_created = on_created
    event_handler.on_deleted = on_deleted
    event_handler.on_modified = on_modified
    event_handler.on_moved = on_moved

    path = "/mnt/c/Users/marke/Desktop"

    if os.path.exists(path):
        print("Path exists")
    else:
        print("Path does not exist")
        sys.exit(1)

    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    print("Observer started")
    observer.start()

    try:
        while True:
            print("Monitoring")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopped monitoring")
        observer.stop()
        print("Stopped monitoring")

    observer.join()
