# https://thepythoncorner.com/posts/2019-01-13-how-to-create-a-watchdog-in-python-to-look-for-filesystem-changes/
# import time
# from watchdog.observers import Observer
# from watchdog.events import PatternMatchingEventHandler


#  1def on_created(event):
#  2    print(f"hey, {event.src_path} has been created!")
#  3
#  4def on_deleted(event):
#  5    print(f"what the f**k! Someone deleted {event.src_path}!")
#  6
#  7def on_modified(event):
#  8    print(f"hey buddy, {event.src_path} has been modified")
#  9
# 10def on_moved(event):
# 11    print(f"ok ok ok, someone moved {event.src_path} to {event.dest_path}")

# if __name__ == "__main__":
#     patterns = ["*"]
#     ignore_patterns = None
#     ignore_directories = False
#     case_sensitive = True
#     my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)


import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()