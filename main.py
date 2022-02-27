import sounddevice as sd
import soundfile as sf
from scipy.io.wavfile import write
import re, queue, sys, tempfile, numpy, threading
from os import system, path, remove, listdir

assert numpy

TRANSCRIPT = "transcript.txt"
AUDIO_PATH = "wavs"
TEXT_FILE = path.join("text", "natgeo.txt")
LOG_FILE = "log.txt"

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, file = sys.stderr)
    q.put(indata.copy())

# AI Model must be mono, with a frequency of 22 khz
def recordAudio(i, running):
   with sf.SoundFile(path.join(AUDIO_PATH, str(i) + ".wav"), mode = 'x', samplerate = 22050,
                      channels = 1) as file:
        with sd.InputStream(samplerate = 22050, device = 1,
                            channels = 1, callback = callback):
            while running.is_set():
                file.write(q.get())

def purgeShort():
    wavs = listdir(AUDIO_PATH)

    for i in range(len(wavs)):
        if wavs[i].endswith(".wav"):
            wf = sf.SoundFile("wavs/" + wavs[i])
            tf = open(TRANSCRIPT, 'r+')

            lines = tf.readlines()

            if (f.frames / f.samplerate) < 3:
                remove(AUDIO_PATH + "/" + wavs[i])
                del lines[i]
                print("[!] Removed recording [" + str(i) + "], too short.")

        tf.seek(0)
        tf.truncate()
        tf.writelines(lines)

        wf.close()
        tf.close()

sentences = []

with open(TEXT_FILE, 'r', encoding = "utf8") as f:
    sentences = re.split('(?<=[.!?]) +', ''.join(f.readlines()).replace("\n", " "))

sentences = [sentences[i] + sentences[i + 1] + " " for i in range(0, len(sentences), 2)]

print("[*] This bot aims to help you more efficiently train your machine learning audio model.")
input("[!] Press enter to start recording...\n")

startIndex = 0

with open(LOG_FILE, 'r') as f:
    firstLine = f.readline()

    if firstLine != "":
        answer = input("[!] You have already recorded audio. Do you want to continue from that point or restart? (y/n) ")
        
        if answer == "y":
            startIndex = int(firstLine)
        elif answer == "n":
            pass
        else:
            print("\nAn unknown answer was given. Exiting...")
            sys.exit()

for i in range(startIndex, len(sentences)):
    try:
        transcript = open(TRANSCRIPT, 'a', encoding = "utf8")
        log = open(LOG_FILE, 'w', encoding = "utf8")

        system("cls")

        print(("#" * 20) + " SENTENCE " + str(i) + " " + ("#" * 20))
        print("\n" + sentences[i] + "\n")
        print("#" * 50)
        print("")

        if path.isfile(path.join(AUDIO_PATH, str(i) + ".wav")):
            remove(path.join(AUDIO_PATH, str(i) + ".wav"))

        running = threading.Event()
        running.set()
        t = threading.Thread(target = recordAudio, args = (i, running,))
        t.start()

        print("[-->] Press enter to continue to next sentence...")
        print("[--X] Or enter 'p' to pause...\n")

        next = input()

        running.clear()
        t.join()

        if next == "p":
            print("\n[!] Paused recording.")
            print("Press enter to continue...")
            input()

        transcript.write(str(path.join(AUDIO_PATH, str(i) + ".wav")) + "|" + sentences[i] + "\n")
        log.write(str(i) + "\n")

    except KeyboardInterrupt:
        print("\n\n[!] Exiting...\n")

        purgeShort()
        
        running.clear()
        t.join()
        break

transcript.close()
log.close()
