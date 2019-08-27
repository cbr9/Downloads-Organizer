#!/usr/bin/python

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import os
import shutil
import time
import imghdr


class Handler(FileSystemEventHandler):
	def __init__(self):
		self.__HOME = os.environ["HOME"]
		self.pdf_dst = os.path.join(self.__HOME, "Documents")
		self.img_dst = os.path.join(self.__HOME, "Pictures")
		self.tracked = os.path.join(self.__HOME, "Downloads")
		os.chdir(self.tracked)

	def on_modified(self, event):
		if os.path.isfile(event.src_path):
			_, extension = os.path.splitext(event.src_path)
			if extension == ".pdf":
				self.move_file(src=event.src_path, dst=self.pdf_dst)
			elif imghdr.what(event.src_path):
				if not event.src_path.endswith(".part"):
					self.move_file(src=event.src_path, dst=self.img_dst)

	@staticmethod
	def move_file(src, dst):
		file = os.path.basename(src)
		dst = os.path.join(dst, file)
		shutil.move(src=src, dst=dst)


event_handler = Handler()
observer = Observer()
observer.schedule(event_handler, event_handler.tracked, recursive=True)
observer.start()

try:
	while True:
		time.sleep(10)
except KeyboardInterrupt:
	observer.stop()
	observer.join()


