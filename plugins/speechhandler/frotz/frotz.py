# -*- coding: utf-8 -*-
import os.path
import pdb
import textPlayer as tp
from jasper import app_utils
from jasper import plugin

class FrotzPlugin(plugin.SpeechHandlerPlugin):
    def get_phrases(self):
        return [
            self.gettext("BEGIN SIMULATION ZORK ONE"),
            self.gettext("BEGIN SIMULATION A MIND FOREVER VOYAGING"),
            self.gettext("BEGIN SIMULATION HITCHHIKERS GUIDE"),
            self.gettext("BEGIN SIMULATION")
            ]
    
    def handle(self,text,conversation):
        self._mic=conversation.mic
        self._logger=conversation._logger
        #pdb.set_trace()
        game="zork1"
        game_name="zork one"
        if( "A MIND FOREVER VOYAGING" in text ):
            game="AMFV"
            game_name="a mind forever voyaging"
        if( "HITCHHIKERS" in text ):
            game="h2g2"
            game_name="the hitchhiker's guide to the galaxy"
        self._mic.say(self.gettext("beginning simulation "+game_name))
        #active_stt_slug = conversation.config['stt_engine']
        #frotz_stt_plugin_info = conversation.application.plugins.get_plugin(active_stt_slug, category='stt')
        #frotz_stt_plugin = frotz_stt_plugin_info.plugin_class('default', self.brain.get_plugin_phrases(), frotz_stt_plugin_info,conversation.config)

        #while( True ):
        #    text=frotz_listen()
        #    print( text )
        #    if( text==["END SIMULATION"] ):
        #        break
        #    mic.say(str(text))
        
        # open zork1.corpus in the current directory and create a phrase list from it
        corpus = os.path.join(os.path.dirname(os.path.realpath(__file__)),"games",game+".corpus")
        phrases=['END SIMULATION']
        with open(corpus, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                phrases.append(line)

        self._logger.debug('Starting frotz mode...')
        with self._mic.special_mode(game, phrases):
            self._logger.debug('Frotz mode started.')
            t = tp.textPlayer(game+'.z5')
            response = t.run()
            current_location=response.location
            self._mic.say(response.location)
            if( response.description ):
                self._mic.say(response.description)
            
            mode_not_stopped = True
            while mode_not_stopped:
                texts = self._mic.active_listen(indicator=0)

                text = ''
                if texts:
                    text = ', '.join(texts).upper()

                if not text:
                    #mic.say(_('Pardon?'))
                    continue

                print( "Text: text" )
                response = t.execute_command(text)
                if( text==["END SIMULATION"] ):
                    mode_not_stopped = False
                else:
                    say_location=False
                    # You don't have to state the location at the beginning of each response
                    # For the most part, I only need a location update when 
                    if( current_location!=response.location ):
                        current_location=response.location
                        say_location=True
                    if( !response.description ):
                        say_location=True
                    if( say_location ):
                        self._mic.say(response.location)
                    if( response.description ):
                        self._mic.say(response.description)

        mic.say(self.gettext('Ending simulation'))
        self._logger.debug("Frotz mode stopped.")

    # Originally I thought I would have to implement my own version of listen() in order to change
    # the language model/dictionary in use. Then I figured out how to use the mic_special_mode to
    # accomplish this. So this is vestigial, but I'm not quite ready to get rid of it yet.
    def frotz_listen(self, timeout=3):
        # record until <timeout> second of silence or double <timeout>.
        n = int(round((self._mic._input_rate/self._mic._input_chunksize)*timeout))
        frames = []
        for frame in self._input_device.record(self._mic._input_chunksize,
                                               self._mic._input_bits,
                                               self._mic._input_channels,
                                               self._mic._input_rate):
            frames.append(frame)
            if len(frames) >= 2*n or (
                    len(frames) > n and self._snr(frames[-n:]) <= 3):
                break
        with self._mic._write_frames_to_file(frames) as f:
            return self.frotz_stt_engine.transcribe(f)
    
    def is_valid(self, text):
        """
        Returns True if the input is related to jokes/humor.

        Arguments:
        text -- user-input, typically transcribed speech
        """
        return any(p.lower() in text.lower() for p in self.get_phrases())
