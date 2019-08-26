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
		self.tracked_folder = os.path.join(self.__HOME, "Downloads")
		os.chdir(self.tracked_folder)

	def on_modified(self, event):
		global src, file
		for root, dirs, files in os.walk(os.getcwd(), topdown=True):
			for file in files:
				_, extension = os.path.splitext(file)
				src = os.path.join(root, file)
				if extension == ".pdf":
					self.move_file(dst=self.pdf_dst)
				elif imghdr.what(src):
					if src.endswith(".part"):
						time.sleep(10)
						src = src.strip("part").strip(".")
					self.move_file(dst=self.img_dst)

	@staticmethod
	def move_file(dst):
		dst = os.path.join(dst, file)
		shutil.move(src, dst=dst)


event_handler = Handler()
observer = Observer()
observer.schedule(event_handler, event_handler.tracked_folder, recursive=True)
observer.start()

try:
	while True:
		time.sleep(10)
except KeyboardInterrupt:
	observer.stop()
	observer.join()
