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


import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Watcher:

    def on_created(self, event):
        print(f"hey, {event.src_path} has been created!")
    
    def on_deleted(self, event):
        print(f"what the f**k! Someone deleted {event.src_path}!")
    
    def on_modified(self, event):
        print(f"hey buddy, {event.src_path} has been modified")
    
    def on_moved(self, event):
        print(f"ok ok ok, someone moved {event.src_path} to {event.dest_path}")
        
    def __init__(self, directory=".", handler=FileSystemEventHandler()):
        self.observer = Observer()
        self.handler = handler
        self.directory = directory
        
        # monkey patch handler
        self.handler.on_created = self.on_created
        self.handler.on_deleted = self.on_deleted
        self.handler.on_modified = self.on_modified
        self.handler.on_moved = self.on_moved
        

    def run(self):
        self.observer.schedule(
            self.handler, self.directory, recursive=True)
        self.observer.start()
        print("\nWatcher Running in {}/\n".format(self.directory))
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
        self.observer.join() # Wait until the thread terminates.
        print("\nWatcher Terminated\n")


class MyHandler(FileSystemEventHandler):

    def on_any_event(self, event):
        if event.event_type == "deleted":
                    print("Oh no! It's gone!")
        if event.src_path[-5:] == ".xml":
                    print("Microsoft Word documents not supported.")                
        print(event) # Your code here

if __name__=="__main__":
    w = Watcher(".", MyHandler())
    w.run()
