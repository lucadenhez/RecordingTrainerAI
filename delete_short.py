from os import listdir, remove
import soundfile as sf

wavs = listdir("wavs")

for i in range(len(wavs)):
    if wavs[i].endswith(".wav"):
        with sf.SoundFile("wavs/" + wavs[i]) as f:
            if (f.frames / f.samplerate) < 3:
                # remove("wavs/" + wavs[i])
                print("Removed: " + wavs[i])
            f.close()
