from threading import Thread

import pat
import patl
import logging
import argparse
import time

from patutils import SEPARATOR, BOX_LENGTH, BASE, USE_SEPARATOR

""" A chat protocol based loosely off IRC
The whole thing works with ASCII256 text
"""
standard_ascii = "\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19" \
                 "\x1a\x1b\x1c\x1d\x1e\x1f !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[" \
                 "\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f"
extended_ascii = "ÇüéâäàåçêëèïîìÄÅÉæÆôöòûùÿÖÜø£Ø×ƒáíóúñÑªº¿®¬½¼¡«»░▒▓│┤ÁÂÀ©╣║╗╝¢¥┐└┴┬├─┼ãÃ╚╔╩╦╠═╬¤ðÐÊËÈıÍÎÏ┘┌█▄¦Ì▀Óß" \
                 "ÔÒõÕµþÞÚÛÙýÝ¯´≡±‗¾¶§÷¸°¨·¹³²■ "
alphabet = standard_ascii + extended_ascii  # python doesn't natively support 'ascii256'

FINISHED = "\x00"
CANCEL = "cancel"
NAME = "name"
TEXT = "text"
# DEBUG = False
logger = logging.getLogger("Debug Window")

parser = argparse.ArgumentParser(description="Sined Messages: Send messages over sound")
parser.add_argument("--debug", dest="debug", action="store_true", default=False)
args = parser.parse_args()
if args.debug: # If debugging
    logger.setLevel(logging.DEBUG) # Set log level to debug
else: # If not
    logger.setLevel(logging.INFO) # Set it to info


class ChatClient:
    playing = False # Whether the client is playing
    override = None # Any overrides
    separated = False # Whether the mmessages are separated (helps reduce loss of 'packets')

    started_count = False #These are used to determine how quickly data is being transmitted
    ended_count = False
    start_time = None
    count_time = 0
    end_time = None
    speed = None

    last = -1

    def handle_name(self, raw_args): # Handles the name command
        old_name = self.other_name # The old name
        self.other_name = raw_args # Sets the new name
        self.action(f"{old_name} has changed their name to {self.other_name}")

    def handle_text(self, raw_args): # Hansles the text
        self.message(self.other_name, raw_args) # Sends message

    commands = {
        TEXT: handle_text, # Handles text command
        NAME: handle_name # Handles NAME command 
    }
    requests = {
        NAME: lambda self, _: self.play_string(f"{NAME}:{self.name}{FINISHED}"), # Responds to NAME request
        TEXT: lambda self, _: self.play_string(f"{TEXT}:{FINISHED}") # Responds to request for text
    }
    buffer = []
    pre_buff = []

    def __init__(self, name="Client 0", other_name="other", buffer=()):
        self.handle_thread = None
        self.name = name
        self.other_name = other_name
        self.buffer = list(buffer)

    def start(self):
        patl.start_listener(self.chat_listener) # Starts the chat listener

    def chat_listener(self, value):
        if self.playing: # If playing
            return # Do nothing
        if self.override: # If there's an override
            return self.override(value) # Use the override
        if USE_SEPARATOR: # If using a separator
            if value == SEPARATOR:
                self.separated = True # Now Separated
                return
            if not self.separated and (self.last == value or self.last == -1): # If not separated
                return

        logger.debug(f"received {value}")
        self.pre_buff.append(value) # Adds to first buffer
        self.separated = False
        logger.debug(f"{self.buffer} & {self.pre_buff}")
        if len(self.pre_buff) == BOX_LENGTH:  # If the first buffer reaches the target size
            decoded = alphabet[base_decode(self.pre_buff, BASE)] # Decodes the characther
            if not self.started_count: # Works out the speed
                print("start")
                self.start_time = time.time()
                self.started_count = True
            self.count_time += 1
            if self.started_count and self.count_time == 10:
                self.end_time = time.time()
                self.speed = self.end_time - self.start_time
                self.started_count = False

                print(f"Speed per 10 Bytes: {self.speed} --> {int(self.speed)}")
            self.pre_buff = []
            if decoded == FINISHED: # If finished
                self.start_handle_thread() # Handle received text
            else: # If not finished
                self.buffer.append(decoded) # Add that to the buffer 

    def handle(self):
        buffer = ''.join(self.buffer) # Joins the characters
        self.buffer = []
        has_command = False # If it has a command
        has_request = False # If it has a request
        command_name = ""
        position = 0
        while not (has_command or has_request):
            try:
                char = buffer[position] # Get the character
            except IndexError:
                continue
            if char == ":": # If a ':'
                has_command = True # It's a command
                continue
            if char == "?": # If a '?'
                has_request = True # It's a request
                continue
            command_name += char # Add the character to the command name
            position += 1 
        raw_args = ''.join(buffer[position + 1:])
        logger.debug(f"COMMAND: {command_name} (`{raw_args}`)")
        if has_command: # If has received a command
            self.commands[command_name](self, raw_args) # Deal with the command
        if has_request: # If has received a request
            self.requests[command_name](self, raw_args) # Deal with the request
        self.clean_handle_thread()

    def play_value(self, value): # Sends the value using the utils
        logger.debug(f"sending {value}")
        self.playing = True
        if USE_SEPARATOR:
            pat.play_value(SEPARATOR)
        pat.play_value(value)
        self.playing = False

    def play_buffer(self, buffer): # sends a buffer
        [self.play_value(value) for value in buffer]

    def play_char(self, char): # Sends a character
        [self.play_value(value) for value in base_encode(char, BASE)]

    def play_string(self, string): # Sends a string
        [self.play_char(char) for char in string]

    def request(self, value: str, raw_args=""): # Sends a request
        self.play_string(value + "?:" + raw_args + FINISHED)

    def command(self, value: str, raw_args=""): # Sends a command
        self.play_string(value + ":" + raw_args + FINISHED)

    def start_handle_thread(self): # Starts the handle thread
        thread = Thread(target=self.handle)
        thread.start()
        self.handle_thread = thread

    def clean_handle_thread(self): # Cleans the handle thread
        self.handle_thread = None

    def action(self, action_message): # When receiving an action
        print("*" + action_message)  # TODO

    def message(self, sender, message): # When receiving a message
        print(f"{sender}: {message}")


def base_encode(number, base): # Encodes to send
    if type(number) == str:
        assert len(number) == 1
        number = alphabet.index(number)
    d = []
    while number != 0:
        d.append(number % base)
        # number -= (number // high) * high
        number //= base
    while len(d) != BOX_LENGTH:
        d.append(0)
    return d[::-1]


def base_4_encode(number): # Encodes to be sent (I think this is unused)
    if type(number) == str:
        assert len(number) == 1
        number = alphabet.index(number)
    d = []
    high = number - number % 4
    while number != 0:
        d.append(number % 4)
        # number -= (number // high) * high
        number //= 4
    while len(d) != BOX_LENGTH:
        d.append(0)
    return d[::-1]


def base_decode(buffer, base): # Decodes the received buffer
    buffer = buffer[::-1]
    total = 0
    for place in range(len(buffer)):
        # print(f"{buffer[place]}@{place}~{4**place} --> {buffer[place] * 4**place}")  # DEBUG
        total += buffer[place] * base ** place
    return total


def base_4_decode(buffer): # Decodes into base4 (Think this is now unused)
    buffer = buffer[::-1]
    total = 0
    for place in range(len(buffer)):
        # print(f"{buffer[place]}@{place}~{4**place} --> {buffer[place] * 4**place}")  # DEBUG
        total += buffer[place] * 4 ** place
    return total
