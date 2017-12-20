# -*- coding: utf-8 -*-
from jasper import app_utils
from jasper import plugin

class FrotzPlugin(plugin.SpeechHandlerPlugin):
    def get_phrases(self):
        return [self.gettext("BEGIN SIMULATION")]
    
    def handle(self,text,mic):
        mic.say([self.gettext("beginning simulation")])
        while( text!=[self.gettext("END SIMULATION")] ):
            mic.say(text)
            text=mic.active_listen()
        mic.say([self.gettext("ending simulation")])
    
    def is_valid(self, text):
        """
        Returns True if the input is related to jokes/humor.

        Arguments:
        text -- user-input, typically transcribed speech
        """
        return any(p.lower() in text.lower() for p in self.get_phrases())
