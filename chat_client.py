import time
from threading import Thread

import pat
import patl
from enum import Enum, auto
import logging
from chat_protocol import ChatClient, TEXT
from patutils import LENGTH, MIN_VALUE, MAX_VALUE, ReturnCode

paired = False
silence = True  # Not needed, playing other frequency
chat_client: ChatClient = None


class SearchMode(Enum): # Is the device searching or listening
    LISTEN = auto()
    SEARCH = auto()


def ping_thread(): # The thread that sends the ping 
    global silence
    while not paired: # While the device is not paired
        silence = False # THere's something coming from the machine
        pat.play_value(MAX_VALUE, LENGTH) # Send a ping
        silence = True # There is nothing coming from the machine
        time.sleep(LENGTH) # and wait
    return


def pair_listener(value): # This listens for the ping from the other machine
    global paired
    global silence
    global chat_client
    if value == MIN_VALUE: # If it hears a response ping
        paired = True # It's paired
        print("PAIRED!") # Outputs paired
        chat_client = ChatClient() # Creates the client
        chat_client.start() # Starts up the client
        return ReturnCode.EXIT


def device_listener(value): # Listenss for devices
    global chat_client
    global paired
    if value == MAX_VALUE: # If it hears a ping
        pat.play_value(MIN_VALUE, LENGTH) # Play response ping
        paired = True
        print("PAIRED!")
        chat_client = ChatClient() # Creates the client
        chat_client.start() # Starts the client
        return ReturnCode.EXIT


def main(mode: SearchMode):
    if mode == SearchMode.SEARCH: # If searching
        patl.start_listener(pair_listener) # Start the search pair listenr
        thread = Thread(target=ping_thread) # Create the ping thread
        thread.start() # Start the ping thread
        thread.join() # End the ping thread
    elif mode == SearchMode.LISTEN: # If listening
        patl.start_listener(device_listener, join=True) # Start the device listener
    else:
        return -1

    while True:
        if not paired:
            continue
        message = input("[Sined]: ") # Take input
        if message.startswith("/"): # If command
            try:
                raw_command = message[1:].strip() # The command without the '/'
                if raw_command.startswith("?"): # If the command is a request
                    raw_command = raw_command[1:].strip() # The command without the '?'
                    split_command = list(
                        filter(None, raw_command.split(" ")))  # Using filter to filter out the empty parts
                    command = split_command[0] # Get the command
                    raw_args = ':'.join(split_command[1:]) # Prepare to send
                    chat_client.request(command, raw_args) # Send the command
                else:
                    split_command = list(filter(None, raw_command.split(" "))) # Get the command split, to obtain the args
                    command = split_command[0] # Get the command
                    raw_args = ':'.join(split_command[1:]) # Prepare to send
                    chat_client.command(command, raw_args) # Send command
            except IndexError:
                logging.error("Malformed command")
        else:
            chat_client.command(TEXT, message)


if __name__ == "__main__":
    chosen_mode = None
    while not chosen_mode:
        try:
            written = input("[S]earch or [L]isten: ").lower()[0] # Whether searching or listening
            if written == "s":
                chosen_mode = SearchMode.SEARCH # Searching
            if written == "l":
                chosen_mode = SearchMode.LISTEN # Listening

        except IndexError:
            continue
    try:
        print(f"Program terminated with exit code: {main(chosen_mode)}")
    except KeyboardInterrupt:
        print("Goodbye!")
