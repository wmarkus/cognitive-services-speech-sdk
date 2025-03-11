#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
"""
Chatting with Azure OAI and Azure Pronunciation Assessment samples for the Microsoft Cognitive Services Speech SDK
"""

import json
import math
import os
import requests
import sys
import time
import threading
import wave
import string
from typing import Literal

import numpy as np
import soundfile as sf

try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    print("""
    Importing the Speech SDK for Python failed.
    Refer to
    https://docs.microsoft.com/azure/cognitive-services/speech-service/quickstart-python for
    installation instructions.
    """)
    sys.exit(1)


# Set up the subscription info for the Speech Service
speech_key, service_region = "5acbbb5c57a8446888d605db1b7db1da", "eastus"

# Set up the parameters for Azure OAI Services
oai_resource_name = "YourOaiResourceName"
oai_deployment_name = "YourOaiDeploymentName"
oai_api_version = "YourOaiApiVersion"
oai_api_key = "YourOaiApiKey"

sample_width = 2
sample_rate = 16000
channels = 1
reduced_unit = 10000000


def read_wave_header(file_path):
    with wave.open(file_path, 'rb') as audio_file:
        framerate = audio_file.getframerate()
        bits_per_sample = audio_file.getsampwidth() * 8
        num_channels = audio_file.getnchannels()
        return framerate, bits_per_sample, num_channels


def push_stream_writer(stream, filenames, merged_audio_path):
    byte_data = b""
    # The number of bytes to push per buffer
    n_bytes = 3200
    try:
        for filename in filenames:
            wav_fh = wave.open(filename)
            # Start pushing data until all data has been read from the file
            try:
                while True:
                    frames = wav_fh.readframes(n_bytes // 2)
                    if not frames:
                        break
                    stream.write(frames)
                    byte_data += frames
                    time.sleep(.1)
            finally:
                wav_fh.close()
        with wave.open(merged_audio_path, 'wb') as wave_file:
            wave_file.setnchannels(channels)
            wave_file.setsampwidth(sample_width)
            wave_file.setframerate(sample_rate)
            wave_file.writeframes(byte_data)
    finally:
        stream.close()


def merge_wav(audio_list, output_path, tag=None):
    combined_audio = np.empty((0,))
    for audio in audio_list:
        y, _ = sf.read(audio, dtype="float32")
        combined_audio = np.concatenate((combined_audio, y))
        os.remove(audio)
    sf.write(output_path, combined_audio, sample_rate)
    if tag:
        print(f"Save {tag} to {output_path}")


def get_mispronunciation_clip(offset, duration, save_path, merged_audio_path):
    y, _ = sf.read(
        merged_audio_path,
        start=int((offset) / reduced_unit * sample_rate),
        stop=int((offset + duration) / reduced_unit * sample_rate),
        dtype=np.float32
    )
    sf.write(save_path, y, sample_rate)


def strip_end_silence(file_path):
    y, _ = sf.read(file_path, start=0, stop=-int(sample_rate * 0.8), dtype=np.float32)
    sf.write(file_path, y, sample_rate)


def chatting_from_file():
    """Performs chatting with Azure OAI and Azure Pronunciation Assessment asynchronously from audio files.
        See more information at https://aka.ms/csspeech/pa"""

    input_files = ["resources/chat_input_1.wav", "resources/chat_input_2.wav"]
    reference_text = ""
    chat_history = [
        {
            "role": "system",
            "content": (
                "You are a voice assistant, and when you answer questions,"
                "your response should not exceed 25 words."
            )
        }
    ]
    sample_sentence1 = "OK the movie i like to talk about is the cove it is very say phenomenal sensational documentary about adopting hunting practices in japan i think the director is called well i think the name escapes me anyway but well let's talk about the movie basically it's about dolphin hunting practices in japan there's a small village where where villagers fisherman Q almost twenty thousand dolphins on a yearly basis which is brutal and just explain massacre this book has influenced me a lot i still remember the first time i saw this movie i think it was in middle school one of my teachers showed it to all the class or the class and i remember we were going through some really boring topics like animal protection at that time it was really boring to me but right before everyone was going to just sleep in the class the teacher decided to put the textbook down and show us a clear from this document documentary we were shocked speechless to see the
