import pyaudio
import numpy
import time
import logging
from threading import Thread
from patutils import LENGTH, BOUND, TONES, ReturnCode

STOP = False
CHUNK = 2048
RATE = 44100
DEBUG = True

threads = []
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)


def read_data():
    return numpy.fromstring(stream.read(CHUNK), numpy.int16)  # Read data from pyaudio input


def sound_listener(callback=None, args=(), report_empty=False):
    while True:
        if STOP:
            return
        data = read_data()
        # https://stackoverflow.com/questions/6908540/pyaudio-how-to-tell-frequency-and-amplitude-while-recording
        amplitudes = 20 * numpy.log10(numpy.abs(numpy.fft.rfft(data[:CHUNK])))

        # Uses values to determine the type of frequencies available
        frequencies = numpy.linspace(0, RATE / 2, len(amplitudes))

        peak = frequencies[amplitudes.argmax()]  # numpy function grabs max amplitude, applies to frequency
        matches = list(filter(lambda x: abs(x - peak) <= BOUND, TONES))
        if matches:
            if len(matches) > 1:
                logging.warning("** MULTIPLE MATCHES FOUND**")
            corrected = matches[0]
            value = TONES.index(corrected)
            # print(f"freq: {peak}, corrected: {corrected}, value: {value}")  # DEBUG
            if callback:
                if callback(*args, value) == ReturnCode.EXIT:
                    return
        else:
            # print("no value")  # DEBUG
            if callback and report_empty:
                if callback(*args, None) == ReturnCode.EXIT:
                    return
        # time.sleep(LENGTH / 2)  # TODO(Check)


def start_listener(callback=None, args=(), report_empty=False, join = False):
    thread = Thread(target=sound_listener, args=[callback, args, report_empty])
    threads.append(thread)
    thread.start()
    if join:
        thread.join()


if __name__ == "__main__":
    try:
        start_listener()
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("Goodbye!")
    finally:
        STOP = True
        for thread in threads:
            thread.join()
        stream.stop_stream()
        stream.close()
        p.terminate()
