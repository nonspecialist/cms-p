#!/usr/bin/env python

import kivy
kivy.require('1.4.1')
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.event import EventDispatcher
from kivy.clock import Clock
from kivy.graphics import *
from cmspulseox import CmsPulseOx
import time

# concept:
# - we communicate with the UI through lists 
# - lists are populated by a reader process (whether it's getting data 
#   direct from the meter, or from a file).
# - the App has an EventDispatcher which uses a  Clock.schedule_interval to 
#   cause it to poll the lists for new data; when received, it either 
#   creates Events or updates Properties to cause various widgets to 
#   update themselves.
# (This based on a discussion on #kivy on irc.freenode.net)
#

# central EventDispatcher:
#   

class PulseOxEventDispatcher(EventDispatcher):
    def __init__(self, **kwargs):
        self.register_event_type('ready_for_poll')
        super(AppEventDispatcher, self).__init__(**kwargs)

    def ready_for_poll(self):
        pass

class PulseOxWaveform(Widget):
    def __init__(self, **kwargs):
        self.current_x = 0
        super(PulseOxWaveform, self).__init__(**kwargs)

    def update_o2sat(self, sat_pct, o2low):
        # o2sat is a percentage, so calculate it as a percentage
        # of the total canvas height
        o2height = int((sat_pct / 100.0) * self.height)
        print "self.height = %d" % self.height
        print "sat_pct = %d" % sat_pct
        print "put o2sat at %d" % o2height
        with self.canvas:
            if o2low:
                Color(1,0,0)
            else:
                Color(0,1,0)
            Ellipse(
                pos = (self.current_x, o2height),
                size = (10, 10)
            )
            
    def update_waveform(self, height):
        base_height = int(self.height / 2)
        with self.canvas:
            # clear a space in front of the drawn point
            # n = (self.current_x+1) / self.width
            # n = 0
            # Color(n, n, n)
            # Rectangle(
                # pos = (self.current_x, 0),
                # size = (100, self.height)
            # )
            Color(1, 1, 1)
            Ellipse(
                pos = (self.current_x, base_height + height),
                size = (10, 10)
            )
            self.current_x += 1
            # clear the widget
            if self.current_x >= self.width:
                self.canvas.clear()
                self.current_x = 0


class PulseOxApp(App):
    def __init__(self, **kwargs):

        self.pulseox = CmsPulseOx()
        self.pulseox.set_loadfile("dump.pkl")
        # self.pulseox.set_serial()

        super(PulseOxApp, self).__init__(**kwargs)

    def clock_tick(self, dt):
        # This works because pulseox.read() is a generator, but
        # we only want to process one packet at a time otherwise 
        # we risk harming app performance
        for tstamp, packet in self.pulseox.read():
            if self.pulseox.parse(packet):
                # print self.pulseox.dump()
                # updates the various widgets around the outside
                self.pulse_rate.text = str(self.pulseox.pulserate)
                self.strength.text = str(self.pulseox.strength)
                self.search.text = "SEARCH" if self.pulseox.search else ""
                self.seek.text = "SEEK" if self.pulseox.seek else ""
                self.error.text = "ERROR" if self.pulseox.error else ""
                self.beep.text = "BEEP" if self.pulseox.beep else ""
                self.o2sat.text = str(self.pulseox.o2_sat) + " %"

                self.tstamp.text = time.strftime("        %H:%M:%S\n%a %d %b %Y",time.localtime(tstamp))

                self.waveform.update_waveform(self.pulseox.waveform)
                self.waveform.update_o2sat(self.pulseox.o2_sat, self.pulseox.o2_low)
            return
        
    def build(self):

        self.top_layout = BoxLayout(orientation = 'vertical')
        self.l1_layout = BoxLayout(orientation = 'horizontal', size_hint = (1, .9))
        self.bottom_bar_layout = BoxLayout(orientation = 'horizontal', size_hint = (1, .1))
        self.right_bar_layout = BoxLayout(orientation = 'vertical', size_hint = (.2, 1))

        self.top_layout.add_widget(self.l1_layout)
        self.top_layout.add_widget(self.bottom_bar_layout)

        self.waveform = PulseOxWaveform(
            pos_hint = {'top':0}, 
            size_hint = (.8, .9))

        self.strength = Button(text = 'strength')
        self.search = Button(text = 'search')
        self.seek = Button(text = 'seek')
        self.error = Button(text = 'error')
        self.beep = Button(text = 'beep')
        self.tstamp = Button(text = 'time')

        self.bottom_bar_layout.add_widget(self.strength)
        self.bottom_bar_layout.add_widget(self.search)
        self.bottom_bar_layout.add_widget(self.seek)
        self.bottom_bar_layout.add_widget(self.error)
        self.bottom_bar_layout.add_widget(self.beep)
        self.bottom_bar_layout.add_widget(self.tstamp)

        self.pulse_rate = Button(text = 'rate', size_hint = (1, .2), font_size = 18)
        self.o2sat = Button(text = 'O2 sat', size_hint = (1, .2), font_size = 18)
        self.bargraph = Button(text = 'bar', size_hint = (1, .6))

        self.right_bar_layout.add_widget(self.pulse_rate)
        self.right_bar_layout.add_widget(self.o2sat)
        self.right_bar_layout.add_widget(self.bargraph)

        self.l1_layout.add_widget(self.waveform)
        self.l1_layout.add_widget(self.right_bar_layout)

        # fire the clock constantly
        Clock.schedule_interval(self.clock_tick, 0)

        return self.top_layout

    def update_waveform(self, height):
        print "PulseOxApp.update_waveform()"
        self.waveform.update_waveform(height)

PulseOxApp().run()
