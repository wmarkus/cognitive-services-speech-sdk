#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.
"""
Speech recognition samples for the Microsoft Cognitive Services Speech SDK
"""

import json
import string
import time
import threading
import wave
import utils
import sys
import io
import requests

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

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Set up the subscription info for the Speech Service:
speech_key, service_region = "5acbbb5c57a8446888d605db1b7db1da", "eastus"

def speech_recognize_once_from_mic():
    """
    Function to recognize speech once from the microphone.
    """
    # ...function implementation...
