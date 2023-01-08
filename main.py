#!/usr/bin/env python3


import argparse
import os
import time
import whisper

from argparse import ArgumentParser, Namespace
from queue import Queue
from speech_recognition import AudioData, Microphone, Recognizer, UnknownValueError


r = Recognizer()
m = Microphone()

audio_queue: Queue = Queue()


def callibrate_noise_level():
    print("A moment of silence...")
    with m as source:
        r.adjust_for_ambient_noise(source)
    print(f"Set minimum energy threshold to {r.energy_threshold}")


def listen():
    print("Now listening...")
    return r.listen_in_background(m, lambda _, audio: audio_queue.put(audio))


def transcribe(model: str, audio: AudioData):
    try:
        return r.recognize_whisper(audio, model).strip().lower()
    except UnknownValueError:
        print("Could not understand audio")


def process_text(trigger: str, text: str):
    if text.startswith(trigger):
        os.system(f'oi -r "{text[len(trigger):]}" | festival --tts')


def poll(args: Namespace):
    model, trigger = args.model, args.trigger.strip().lower()
    while True:
        if not audio_queue.empty():
            text = transcribe(model, audio_queue.get())
            if text:
                process_text(trigger, text)


def get_args():
    parser = ArgumentParser()
    parser.add_argument("--model", default="tiny.en", help="Model to use",
                        choices=whisper.available_models())
    parser.add_argument("--trigger", default='hey', help="Trigger word")
    return parser.parse_args()


if __name__ == "__main__":
    callibrate_noise_level()
    stop_listening = listen()
    try:
        poll(get_args())
    except KeyboardInterrupt:
        stop_listening()
