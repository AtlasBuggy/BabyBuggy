import time
from subprocess import Popen, PIPE, STDOUT
from signal import SIGINT


class AVItoMP4converter:
    def __init__(self, input_file_path, output_file_path):
        self.process = None
        self.output = None
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path

    def start(self):
        self.stop()

        # cmd = "/usr/local/bin/ffmpeg -i %s -y -vcodec libx264 -preset slow -an -crf 31 %s" % (
        #     self.input_file_path, self.output_file_path
        # )
        cmd = "/usr/bin/ffmpeg -i %s -y -vcodec libx264 %s" % (
            self.input_file_path, self.output_file_path
        )

        # cmd = ["echo $(brazil-bootstrap -p JDK8-1.0)"]
        self.process = Popen(cmd, stdout=PIPE,
                             # stderr=PIPE,
                             bufsize=1,
                             universal_newlines=True, shell=True)

        self.output = None

    @property
    def exitcode(self):
        if self.process is not None:
            return self.process.returncode
        else:
            return None

    def join(self):
        if self.process is not None:
            return self.process.join()

    def is_running(self):
        if self.process is not None:
            # stdoutdata, stderrdata = self.process.communicate()
            # print("stdoutdata: %s, stderrdata: %s" % (stdoutdata, stderrdata))
            # return self.process.returncode

            return self.process.poll() is None
        else:
            return False

    def stop(self):
        if not self.is_running():
            self.process = None

        if self.process is not None:
            self.output = 0
            try:
                self.process.send_signal(SIGINT)
                self.dump_process_output(0.01)

                if self.is_running():
                    self.dump_process_output(1)

                    print("Process is still running...")

                    t0 = time.time()
                    while time.time() - t0 < 3:
                        self.dump_process_output(1)
                        if not self.is_running():
                            break
                        print("Sending interrupt again")
                        self.process.send_signal(SIGINT)

                self.dump_process_output(1)
                # self.process.terminate()
                self.process.wait()  # -> move into background thread if necessary
            except EnvironmentError as e:
                print("can't stop %s: %s", e)
            else:
                self.process = None

    def dump_process_output(self, delay):
        t0 = time.time()
        for line in self.process.stdout:
            print("[avi to mp4 converter] %s" % line)
            if time.time() - t0 > delay:
                break
