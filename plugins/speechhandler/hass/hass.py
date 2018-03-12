# -*- coding: utf-8 -*-
from sys import maxint
import json
import requests
import logging
from jasper import plugin


class HassPlugin(plugin.SpeechHandlerPlugin):
    def get_priority(self):
        return maxint

    def get_phrases(self):
        return []

    def handle(self, text, mic, *args):
        """
        Reports that the user has input for HASS.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        """

        logger = logging.getLogger(__name__)
        HOST = self.profile['hass']['host']
        PASSWD = self.profile['hass']['api_password']

        text = json.dumps(text)
        logger.debug("Sending to HASS: '%s'", text)

        req = requests.post("{}/api/wit?api_password={}".format(HOST,
                            PASSWD), data=text)
        logger.debug("Status: %d %s", req.status_code, req.reason)
        logger.debug(req.text)
        message = None

        try:
            reqJson = json.loads(req.text)
            message = reqJson['speech']
        except:
            message = self.gettext("Error occurred")

        mic.say(message)

    def is_valid(self, text):
        return True
