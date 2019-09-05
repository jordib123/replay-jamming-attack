# replay-jamming-attack
An automated replay and jamming attack against Remote Keyless Entry (RKE) systems in vehicles using software-defined radios.

# Legal warning

This implementation is for EDUCATIONAL PURPOSES ONLY. Don't use it for illegal activities. You are the only responsable for your actions!

# Background

## Replay and jamming attack

The traditional RKE systems in vehicles has been seen as "secure" for the last decades due to their implementation of Rolling or Hopping Code preventing replay attacks. Rolling or Hopping Code ensures that a signal transmitted by the key fob is only accepted once by the vehicle. Therefore, criminals are unable to intercept and capture the signal transmitted by the authorized key fob and retransmit them to gain access to the vehicle. 

By blocking the reception of the vehicle (=jamming) criminals are able to ensure that the vehicle does not correctly receive the signal while capturing the signal themselves. Since the signal is not yet received by the vehicle, the criminals can retransmit it to gain access to the vehicle. Vehicles typically allocate a larger frequency passband than necesarry. Blocking the reception of the car is done by transmitting the jamming signal inside the passband next to the actual operating frequency of the key fob. By using a receiver that filters out the jamming signal, adversaries are able to capture a valid key fob signal without jamming their own receiver.

<p align="center">
  <img width="320" height="300" src="https://raw.githubusercontent.com/jordib123/replay-jamming-attack/master/images/jammer.png">
</p>

The attack is explained below:
  1. **Jam + capture signal 1**: Jam the vehicle while capturing the first transmitted key fob signal.
  2. **Jam + capture signal 2**: The vehicle typically notifies the owner when a signal is correctly received by for example flickering the hazard lights or closing/opening the mirrors. Therefore the victim knows something went wrong. A natural reaction of the victim is to press the button a second time. We jam the vehicle a second time and record the second key fob signal.
  3. **Stop jamming + transmit signal 1**: Immediatly after capturing the second key fob signal, we stop jamming and transmit the first captured key fob signal. Since we stopped jamming, the retransmitted signal will get accepted by the car and (un)lock the doors. The victim thinks the doors are (un)locked by the signalt transmitted on the second button press while in reality the doors are (un)locked by the retransmitted first signal.
  
<p align="center">
  <img width="650" height="225" src="https://raw.githubusercontent.com/jordib123/replay-jamming-attack/master/images/rolljam-diagram.png">
</p>
  
The adversary now has a valid key fob signal with a valid Rolling or Hopping code that can be used to gain access to the vehicle. Note that this attack is feasible against very RKE systems (f.e. remote controlled garage doors or gates) and therefore not restricted to vehicles.

## Countermeasures

Not all vehicles equipped with RKE are vulnerable to this attack. Some vehicles (f.e. 2018 Ford Focus, 2012 Ford C-MAX, ...) utilise the complete frequency passband of the receiver by transmitted signals on multiple frequencies. The key fob transmit a signal at the beginning, center and end of the frequency passband which leaves no place for the adversary to transmit their jamming signal.

The success rate of this attack is highly dependant on the distance between the operating frequency of the key fob and the frequency of the jamming signal. The closer we can transmit the jamming signal to the operating frequency without interferring with the actual authorized key fob signal, the easier it is to jam the receiver. We were unable to correcly jam some cars (f.e. 2018 Mazda CX5) by transmitting a jamming signal next to the operating frequency of the key fob. Only when jamming directly on the key fob signal, the vehicle is jammed. However doing so, the key fob signal is corrupted and can't be used by adversaries.

# Requirements

## Software

The attack is implemented using GNU Radio (https://www.gnuradio.org/) and gr-osmosdr (https://osmocom.org/projects/gr-osmosdr/wiki) to control the software defined radios. It is possible to execute the attack using a Raspberry Pi. However we were unable to execute it on the Raspbian operating system due to Python memory corruption errors introduced by the gr-osmosdr package. By installing Ubuntu Mate as the OS of the Raspberry Pi, we were able to correctly execute the attack. 
 
## Hardware

The attack requires a receiving and transmitting software-defined radio. In our case we used to RTL-SDR (https://www.rtl-sdr.com/buy-rtl-sdr-dvb-t-dongles/) to receive the key fob signals and the HackRF One (https://greatscottgadgets.com/hackrf/one/) to transmit the jamming and key fob signals. Alternativaly a full-duplex software-defined radio can be used, however we did not test this.

# Execution

The attack can be executed using GNU Radio Companion or via the terminal using Python:

  1. **GNU Radio Companion**: The attack can be executing by opening the _replay-jamming.grc_ in GNU Radio Companion, the graphical interface of GNU Radio.
  2. **Python via terminal**: "Python replay-jamming.py" executes the attack via the terminal. By default the transmit frequency of the jamming signal is 433.85 MHz while the center listening frequency is 433.92 MHz with a 100 kHz boundary ([433.87Mhz;433.97Mhz]). It is possible to modify these values by editing _replay-jamming.py_.
