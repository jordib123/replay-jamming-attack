"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
import sched, time
import osmosdr
from gnuradio import gr


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    def __init__(self, sink='signal.raw'):
        gr.sync_block.__init__(
            self,
            name='Custom File Sink', 
            in_sig=[np.complex64, np.complex64, np.float32],
            out_sig=[np.complex64]
        )
        self.first_signal = None
        self.sink = open(sink, 'w+b')
        self.first_signal_captured = False
        self.detected = False
        self.transmit = False
        self.finished = False
        self.timer = 0


    def work(self, input_items, output_items):
        input_jam = input_items[0] # Jamming signal
        input_sig = input_items[1] # Osmocom captured signal
        input_detect = input_items[2] # Signal detection

        # Transmit first captured key fob signal
        if self.transmit:
            output_items[0][:] = self.transmit_signal(len(output_items[0]))
        else:
            output_items[0][:] = input_jam 

        if not self.finished:
            self.process_input(input_detect, input_sig)

        return len(output_items[0])


    def process_input(self, input_detect, input_sig):
        """
        Function checks if a key fob signal is detected (1 in input_detect).
        If True, save first packet of input signal (key fob signal) and set 'detected' Boolean to True (for 1 second).
        If key fob signal was already detected in previous packets ('detected' = True), save input packet to corresponding sink.
        
        Parameters:
            input_detect (np.ndarray): input signal used for detection of the key fob signal
            input_sig (np.ndarray): raw radio frequency signal captured by SDR
        """
        if self.detected:
            self.save(input_sig)
            self.check_timer()
        elif 1 in input_detect:
            if self.first_signal_captured:
                self.sink.write(bytearray(input_sig))
                self.transmit = True
            else:
                self.first_signal = input_sig
            self.start_timer()


    def transmit_signal(self, length):
        """
        Function creates np.ndarray of length 'length' parameter consisting of the first captured key fob signal.
        
        Parameters:
            length (int): length of output_items array

        Returns:
            np.ndarray: ndarray consisting of captured key fob signal (+ additional padding if captured key fob signal is to short for packet)
        """
        result = np.pad(self.first_signal[:length], (0, length - len(self.first_signal[:length])), 'constant')
        self.first_signal = self.first_signal[length:]
        return result


    def save(self, data):
        """
        Function saves input signal to corresponding sink:
        First key fob signal is saved to variable
        Second key fob signal is saved to file (for later use)
        
        Parameters:
            data (np.ndarray): input signal that has to be saved
        """
        if not self.first_signal_captured:
            self.first_signal = np.concatenate((self.first_signal, data))
        else:
            self.sink.write(bytearray(data))


    def start_timer(self):
        """Function starts timer upon detecting a key fob signal"""
        self.timer = int(round(time.time() * 1000))
        self.detected = True


    def check_timer(self):
        """
        Function checks if timer's value > 1000 ms:
        If timer > 1000, stop saving the input signal
        If timer < 1000, do nothing (=keep saving input signal)
        """
        curr_time = int(round(time.time() * 1000))
        if (curr_time - self.timer) >= 1000:
            print('Signal captured')
            if self.first_signal_captured:
                self.sink.close()
                self.finished = True
            self.detected = False 
            self.first_signal_captured = True

