import ast
from twilio.rest import Client
import configparser
from utils import truthy
from utils import logger
from datetime import datetime
# import telegram
import logging
import requests
import json
# from telegram import Update
# from telegram.ext import Updater, CommandHandler, CallbackContext
from insultgenerator import phrases

class Communicator:
    def __init__(self):
        self.reset()
        self.load()

    def send_telegram_message(self):
        response = {}
        api_key = self.comms['telegram_bot_token']
        headers = {'Content-Type': 'application/json',
                   'Proxy-Authorization': 'Basic base64'}
        data_dict = {'chat_id': self.comms['telegram_groupID'],
                     'text': self.msg,
                     'parse_mode': 'HTML',
                     'disable_notification': True}
        data = json.dumps(data_dict)
        url = f'https://api.telegram.org/bot{api_key}/sendMessage'

        response = requests.post(url,
                                 data=data,
                                 headers=headers,
                                 verify=False)
        return response

    def reset(self):
        self.comms = {'twilio_enabled': False,
                      'twilio_sid': '',
                      'twilio_token': '',
                      'twilio_fromphone': '',
                      'twilio_tophones': [],
                      'telegram_enabled': False,
                      'telegram_bot_token': '',
                      'telegram_groupID': '',
                      'telegram_intro': ''
                      }

    def load(self):
        config = configparser.RawConfigParser()
        config.read('comms-example.ini')

        try:
            twilio = dict(config["twilio"])
            tonumbers = config.get("tonumbers", "tophone")
            tonumbers = ast.literal_eval(tonumbers)
            telegram_info = dict(config["telegram"])

            self.comms['twilio_enabled'] = truthy(twilio['enabled'])
            self.comms['twilio_sid'] = twilio['sid']
            self.comms['twilio_token'] = twilio['token']
            self.comms['twilio_fromphone'] = twilio['fromphone']
            self.comms['twilio_tophones'] = tonumbers
            self.comms['telegram_enabled'] = truthy(telegram_info['enabled'])
            self.comms['telegram_bot_token'] = telegram_info['token']
            self.comms['telegram_groupID'] = telegram_info['group']
            self.comms['telegram_intro'] = telegram_info['intro']

        except KeyError:
            raise KeyError()

    def msg(self, method, msg):

        # datetime object containing current date and time
        now = datetime.now()
        message = ''
        # dd/mm/YY H:M:S
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        logger.info(dt_string + '-' + msg)
        if method == 'SMS' or method == 'BOTH':
            if self.comms['twilio_enabled']:
                client = Client(self.comms['twilio_sid'], self.comms['twilio_token'])
                if isinstance(self.comms['twilio_tophones'], list):
                    for number in self.comms['twilio_tophones']:
                        message = client.messages.create(
                            body=self.comms['telegram_intro'] + msg,
                            from_=self.comms['twilio_fromphone'],
                            to=number
                        )
                else:
                    message = client.messages.create(
                        body=self.comms['telegram_intro'] + msg,
                        from_=self.comms['twilio_fromphone'],
                        to=self.comms['twilio_tophones'][0]
                    )
                logger.debug("twilio message-id" + message.sid)

        if method == 'telegram' or method == 'BOTH':
            if self.comms['telegram_enabled']:
                try:
                    self.msg = self.comms['telegram_intro'] + ': ' + msg
                    resp=self.send_telegram_message()
                except Exception as e:
                    logger.setLevel(logging.DEBUG)
                    logger.debug('Error: sending message to Telegram Group')
                    logger.debug("telegram response: " + str(e))

                else:
                    logger.debug("telegram message success: ")
        return

