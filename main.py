import sounddevice as sd
import soundfile as sf
from scipy.io.wavfile import write
import re, queue, sys, tempfile, numpy, threading
from os import system

assert numpy

TRANSCRIPT = "transcript.txt"
AUDIO_PATH = "audio/"
TEXT_FILE = "text/natgeo.txt"

q = queue.Queue()

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(indata.copy())

def recordAudio(i, running):
   with sf.SoundFile(AUDIO_PATH + str(i) + ".wav", mode = 'x', samplerate = 22000,
                      channels = 1) as file:
        with sd.InputStream(samplerate = 22000, device = 1,
                            channels = 1, callback = callback):
            while running.is_set():
                file.write(q.get())

sentences = []

with open(TEXT_FILE, 'r', encoding = "utf8") as f:
    sentences = re.split('(?<=[.!?]) +', ''.join(f.readlines()).replace("\n", " "))

sentences = [sentences[i] + sentences[i + 1] + " " for i in range(0, len(sentences), 2)]

input("[!] Press enter to start recording...")

for i in range(len(sentences)):
    system("cls")

    print(sentences[i] + "\n")
    
    running = threading.Event()
    running.set()

    t = threading.Thread(target = recordAudio, args = (i, running,))
    t.start()

    input("[*] Press enter to continue to next sentence...")
    running.clear()
    t.join()
