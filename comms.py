import ast
from twilio.rest import Client
import configparser
from utils import truthy
from utils import logger
from datetime import datetime
import telegram
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from insultgenerator import phrases


class Communicator:
    def __init__(self):
        self.reset()
        self.load()

        self.telegram = telegram.Bot(token=self.comms['telegram_bot_token'])
        self.telegram.updater = Updater(token=self.comms['telegram_bot_token'])
        self.telegram.dispatcher = self.telegram.updater.dispatcher

        insult_handler = CommandHandler('insult', self.insulter)
        self.telegram.dispatcher.add_handler(insult_handler)

        balance_handler = CommandHandler('insult', self.balance_reporter)
        self.telegram.dispatcher.add_handler(balance_handler)

        txns_handler = CommandHandler('insult', self.txns)
        self.telegram.dispatcher.add_handler(txns_handler)

        help_handler = CommandHandler('help', self.help)
        self.telegram.dispatcher.add_handler(help_handler)


        self.telegram.updater.start_polling()
        self.command = {'new': False,
                        'user': '',  # the username of the person commanding the bot
                        'balance': 0,
                        'txns': ' ',
                        'help': False}  # will place an order for x Divi right under lowest sell price

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
        config.read('comms.ini')

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
                    msg = self.comms['telegram_intro'] + ': ' + msg
                    self.telegram.send_message(text=msg, chat_id=self.comms['telegram_groupID'])
                except Exception as e:
                    logger.setLevel(logging.DEBUG)
                    logger.debug('Error: sending message to Telegram Group')
                    logger.debug("telegram response: " + str(e))

                else:
                    logger.debug("telegram message success: ")
        return

    def insulter(self, update: Update, context: CallbackContext):
        if len(context.args) == 0:
            target = update.message.from_user.username
        else:
            target = context.args[0]

        insult = phrases.get_so_insult_with_action_and_target(str(target), 'he')
        context.bot.send_message(chat_id=update.effective_chat.id, text=insult)
        logger.debug(context.bot.username)

    def balance_reporter(self, update: Update, context: CallbackContext):
        self.command['new'] = True
        self.command['user'] = update.message.from_user.username
        self.command['whoseup'] = True
        logger.debug(self.command['user'])

    def txns(self, update: Update, context: CallbackContext):
        self.command['new'] = True
        self.command['user'] = update.message.from_user.username
        self.command['whoseup'] = True
        logger.debug(self.command['user'])

    def help(self, update: Update, context: CallbackContext):
        self.command['new'] = True
        self.command['user'] = update.message.from_user.username
        self.command['help'] = True
        logger.debug(self.command['user'])
