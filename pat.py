#!/usr/bin/env python
from patutils import TONES, LENGTH, CHUNK_SIZE
import pysine

if __name__ == "__main__":
    while True:
        for tone in TONES:
            pysine.sine(tone, LENGTH)


def play_tone(tone, length=LENGTH):
    pysine.sine(tone, length)


def play_value(value, length=LENGTH):
    pysine.sine(TONES[value], length)
