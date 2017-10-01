import os
import time
from avi_to_mp4 import AVItoMP4converter
from multiprocessing import Value, Lock, cpu_count

converted_ext = ".mp4"
converted_dir = "converted"
raw_ext = ".avi"
raw_dir = "videos"


class ProcessManager:
    def __init__(self):
        self.queued_conversions = []
        self.conversion_processes = []
        self.video_write_lock = Lock()
        self.notified = False

        # self._num_conversions = Value('i', 0)
        self._completed_conversions = Value('i', 0)

    @property
    def completed_conversions(self):
        with self._completed_conversions.get_lock():
            return self._completed_conversions.value

    def add_parse_process(self, in_path, out_path):
        self.queued_conversions.append((in_path, out_path))
        print("%s queued conversions" % len(self.queued_conversions))

    def update(self):
        if self.check_active_processes():
            self.start_conversion_process()

        with self._completed_conversions.get_lock():
                print(
                    "%s conversions complete!" % (
                        self._completed_conversions.value)
                )
                # self.notified = True

    def check_active_processes(self):
        alive_processes = []
        for process in self.conversion_processes:
            if process.is_running():
                alive_processes.append(process)
            else:
                with self._completed_conversions.get_lock():
                    self._completed_conversions.value += 1

        print("num alive:", len(alive_processes))
        self.conversion_processes = alive_processes

        return len(self.conversion_processes) < cpu_count()

    def start_conversion_process(self):
        while len(self.conversion_processes) < cpu_count() and len(self.queued_conversions) != 0:
            in_path, out_path = self.queued_conversions.pop(0)

            process = AVItoMP4converter(in_path, out_path)
            process.start()

            self.conversion_processes.append(process)
            print("%s conversion processes running. Adding another" % len(self.conversion_processes))
        # print("%s conversion processes running." % len(self.conversion_processes))

        self.notified = False

    def join_processes(self):
        # with self._completed_conversions.get_lock(), self._num_conversions.get_lock():
        #     if self._completed_conversions.value < self._num_conversions.value:
        #         print("Waiting for conversions to finish...")
        for process in self.conversion_processes:
            process.join()


def find_converted_paths():
    converted_paths = []
    for dirpath, dirnames, filenames in os.walk(converted_dir):
        for filename in filenames:
            if filename.endswith(converted_ext):
                converted_paths.append(os.path.join(dirpath, filename))
    return converted_paths


def split_folders(path):
    folders = []
    while True:
        path, folder = os.path.split(path)

        if folder != "":
            folders.append(folder)
        else:
            if path != "":
                folders.append(path)

            break

    folders.reverse()
    return folders


def convert_raw_videos():
    t0 = time.time()
    converted_paths = find_converted_paths()
    paths_to_convert = []
    print(converted_paths)
    for dirpath, dirnames, filenames in os.walk(raw_dir):
        for filename in filenames:
            if filename.endswith(raw_ext):
                path = os.path.join(dirpath, filename)
                filename = filename[:-len(raw_ext)] + converted_ext
                relative_paths = split_folders(path)[1:-1]

                directory = os.path.join(converted_dir, *relative_paths)
                converted_path = os.path.join(directory, filename)

                if converted_path not in converted_paths:

                    if not os.path.isdir(directory):
                        os.mkdir(directory)

                    paths_to_convert.append((path, converted_path))

    manager = ProcessManager()
    for raw_path, converted_path in paths_to_convert:
        manager.add_parse_process(raw_path, converted_path)

    while manager.completed_conversions != len(paths_to_convert):
        manager.update()
        time.sleep(1)
        print("completed: %s of %s" % (manager.completed_conversions, len(paths_to_convert)))

    t1 = time.time()
    print("took: %0.4fs" % (t1 - t0))


convert_raw_videos()

# manager = ProcessManager()
# manager.add_parse_process("videos/2017_Sep_29/19_12_08.avi", "converted/2017_Sep_29/19_12_08.mp4")
# while manager.completed_conversions != 1:
#     manager.update()
#     time.sleep(1)
#     print("completed: %s of 1" % (manager.completed_conversions))