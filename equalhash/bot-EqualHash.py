#!/usr/bin/python3
# -*- coding: utf-8 -*-

import configparser
import json
import logging
import os
import re
from datetime import datetime
import telebot
import urllib3
import requests
from conf.lang import translations
from pymongo import MongoClient
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time

# Go to directory
directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(directory)


# Function for thousand separator
def thousandSep(number):
    return f'{int(number):,}'


# Request to API data
def requestAPI(argUrl):
    try:
        #response = http.request('GET', argUrl)
        response = requests.get(argUrl, verify=False)
        if response.status_code != 200:
            data_json = {"ok": False, "error_code": response.status_code, "description": response.raw}
        else:
            data_json = response.json()
        return data_json

    except Exception as e2:
        data_json = {"ok": False, "description": str(e2)}
        return data_json


# Function user information
def infoUser(message):
    logger.debug("New Message -> idUser: {0}, username: {1}, message: {2}".format(message.from_user.id,
                                                                                  message.from_user.username,
                                                                                  message.text))

    idUser = message.from_user.id
    name = message.from_user.first_name
    lastName = message.from_user.last_name
    username = message.from_user.username
    registrationDate = datetime.utcnow()

    userDocument = {
        '_id': str(idUser),
        'username': username,
        'name': name,
        'lastName': lastName,
        'languageCode': 'en',
        'registrationDate': registrationDate,
        'lastMessage': {
            'type': '',
            'idMessage': '',
            'text': ''
        }
    }

    return userDocument


# Function user information on callback
def infoUserCallback(message):
    logger.debug("New Callback -> idUser: {0}, username: {1}, message: {2}".format(message.from_user.id,
                                                                                   message.from_user.username,
                                                                                   message.data))

    idUser = message.from_user.id
    name = message.from_user.first_name
    lastName = message.from_user.last_name
    username = message.from_user.username
    registrationDate = datetime.utcnow()

    userDocument = {
        '_id': str(idUser),
        'username': username,
        'name': name,
        'lastName': lastName,
        'languageCode': 'en',
        'registrationDate': registrationDate,
        'lastMessage': {
            'type': '',
            'idMessage': '',
            'text': ''
        }
    }
    
    return userDocument


# Function for check if user is new
def checkUser(userDocument):
    # Find the user in the DB
    userDocument2 = userColl.find_one({"_id": userDocument['_id']})
    if userDocument2 is None:
        logger.info("New user: {0}".format(userDocument))
        userColl.insert_one(userDocument)

        return userDocument

    else:
        return userDocument2


# Keyboard to select stats
def keyboardStats1(infoUserDB):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton(translations['statsp2m'], callback_data="statsp2m"),
               InlineKeyboardButton(translations['statsaddr'], callback_data="statsaddr"))
    
    return markup


# Keyboard to return select stats
def keyboardStats2(infoUserCall):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton(translations['return'], callback_data="statsReturn"))

    return markup


# Keyboard to return select stats for address
def keyboardStats3(infoUserCall):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton(translations['return'], callback_data="statsaddr"))

    return markup


# Keyboard to return select stats for myaddrs
def keyboardReturnMyAddrs(infoUserCall):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton(translations['return'], callback_data="myAddrs"))

    return markup


# Keyboard to list address
def keyboardAddress(infoUserCall, addresses, prefix, buttonReturn=True):
    # We get number of addresses and if it's even or odd
    i = addresses.count()
    j = 0
    modI = i % 2

    markup = InlineKeyboardMarkup()
    markup.row_width = 2

    if i == 1:
        markup.add(InlineKeyboardButton(addresses[0]['name'], callback_data=prefix + addresses[0]['address']))

    else:
        # If it's odd
        if modI == 1:
            k = 0
            for j in range(int((i - 1) / 2)):
                markup.add(InlineKeyboardButton(addresses[k]['name'], callback_data=prefix + addresses[k]['address']),
                           InlineKeyboardButton(addresses[k + 1]['name'],
                                                callback_data=prefix + addresses[k + 1]['address']))

                k = k + 2

            markup.add(
                InlineKeyboardButton(addresses[k]['name'], callback_data=prefix + addresses[k]['address']))

        # If it's even
        else:
            k = 0
            for j in range(int(i / 2)):
                markup.add(InlineKeyboardButton(addresses[k]['name'], callback_data=prefix + addresses[k]['address']),
                           InlineKeyboardButton(addresses[k + 1]['name'],
                                                callback_data=prefix + addresses[k + 1]['address']))

                k = k + 2


    # Button to return
    if buttonReturn:
        markup.add(
            InlineKeyboardButton(translations['return'], callback_data="statsReturn"))

    return markup


# Keyboard with options for address (edit, delete, view...)
def keyboardOptionsAddr(infoUserCall, address):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton(translations['viewStats'], callback_data="stats-" + address),
        InlineKeyboardButton(translations['editAddr'],
                             callback_data="editAddr-" + address),
        InlineKeyboardButton(translations['delAddr'], callback_data="delAddr-" + address),
        InlineKeyboardButton(translations['notifications'],
                             callback_data="notAddr-" + address),
        InlineKeyboardButton(translations['return'], callback_data="myAddrs"))

    return markup


# Keyboard confirm delete address
def keyboardDeleteAddres(infoUserCall, address):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton(translations['yesDelAddr'],
                             callback_data="yesDelAddr-" + address),
        InlineKeyboardButton("No", callback_data="myAddrs"))

    return markup


# Keyboard edit configuracion address (name, code)
def keyboardEditAddress(infoUserCall, address):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton(translations['editNameAddr'],
                             callback_data="setNameAddr-" + address),
        InlineKeyboardButton(translations['editCodeAddr'],
                             callback_data="setCodeAddr-" + address))

    return markup


# Keyboard notifications
def keyboardNotifications(address):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("ON", callback_data="notON-" + address),
        InlineKeyboardButton("OFF", callback_data="notOFF-" + address))

    return markup


# ---------- Settings Config ----------
conf = configparser.ConfigParser()
conf.read('conf/EqualHash.conf')
LOG = conf['BASIC']['pathLog']
TOKEN = conf['BASIC']['tokenBot']
MONGOCONNECTION = conf['BASIC']['connectMongoDB']
POOLSTATS = conf['API']['poolStats']
ADDRESSSTATS = conf['API']['addressStats']
FILELOG = bool(conf['BASIC']['fileLog'])
# -------------------------------------
# ---------- Logging ----------
if not os.path.exists('log'):
    os.makedirs('log')

logger = logging.getLogger('EqualHash')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if FILELOG:
    fh = logging.FileHandler(LOG)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)
# -----------------------------

logger.info("--- Start the bot EqualHash ---")

# Object for TelegramBot
bot = telebot.TeleBot(TOKEN)

# Connect to DB
connectDB = MongoClient(MONGOCONNECTION)
db = connectDB.EqualHash
userColl = db.Users
addrCol = db.Addresses

# Object for API request
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager()


# ---------- Comands ----------

# Message for command /start
@bot.message_handler(commands=['start'])
def message_start(message):
    infoUserDB = checkUser(infoUser(message))
    bot.send_message(chat_id=infoUserDB['_id'], text=str(translations['startMessage']),
                     parse_mode='Markdown')


# Message for command /seestats
@bot.message_handler(commands=['seestats'])
def message_seestats(message):
    infoUserDB = checkUser(infoUser(message))
    bot.send_message(chat_id=infoUserDB['_id'], text=str(translations['stats1']),
                     reply_markup=keyboardStats1(infoUserDB))


# Message for command /myaddrs
@bot.message_handler(commands=['myaddrs'])
def message_myaddrs(message):
    infoUserDB = checkUser(infoUser(message))
    logger.debug("Search addresses for user: {0}".format(infoUserDB['_id']))
    addrs = addrCol.find({"idUser": infoUserDB['_id']})
    logger.debug("Send keyboard myAddrs to user: {0}".format(infoUserDB['_id']))

    if addrs.explain()['executionStats']['nReturned'] == 0:
        logger.info("Found 0 Address User: {0}".format(infoUserDB['_id']))
        bot.send_message(chat_id=infoUserDB['_id'],
                         text=u"\u26A0 " + str(translations['noneAddr']))

    else:
        bot.send_message(chat_id=infoUserDB['_id'], text=str(translations['selectAddr']),
                         reply_markup=keyboardAddress(infoUserDB, addrs, 'myaddr-', False))


# Message for command /newaddr
@bot.message_handler(commands=['newaddr'])
def message_newaddr(message):
    infoUserDB = checkUser(infoUser(message))
    response = bot.send_message(chat_id=infoUserDB['_id'], text=str(translations['newAddr']),
                                parse_mode='Markdown')
    userColl.update_one({"_id": str(infoUserDB['_id'])},
                        {"$set": {"lastMessage.type": "newaddr", "lastMessage.idMessage": str(response.message_id)}})


# Message for command /deleteaddr
@bot.message_handler(commands=['deleteaddr'])
def message_deleteaddr(message):
    infoUserDB = checkUser(infoUser(message))
    logger.debug("Search addresses for user: {0}".format(infoUserDB['_id']))
    addrs = addrCol.find({"idUser": infoUserDB['_id']})

    if addrs.explain()['executionStats']['nReturned'] == 0:
        logger.info("Found 0 Address User: {0}".format(infoUserDB['_id']))
        bot.send_message(chat_id=infoUserDB['_id'],
                         text=u"\u26A0 " + str(translations['noneAddr']))

    else:
        bot.send_message(chat_id=infoUserDB['_id'], text=str(translations['delAddrC']),
                         reply_markup=keyboardAddress(infoUserDB, addrs, 'delAddr-', False), parse_mode='Markdown')


# Message for command /setname
@bot.message_handler(commands=['setname'])
def message_setname(message):
    infoUserDB = checkUser(infoUser(message))
    logger.debug("Search addresses for user: {0}".format(infoUserDB['_id']))
    addrs = addrCol.find({"idUser": infoUserDB['_id']})

    if addrs.explain()['executionStats']['nReturned'] == 0:
        logger.info("Found 0 Address User: {0}".format(infoUserDB['_id']))
        bot.send_message(chat_id=infoUserDB['_id'],
                         text=u"\u26A0 " + str(translations['noneAddr']))

    else:
        bot.send_message(chat_id=infoUserDB['_id'], text=str(translations['setnameAddrC']),
                         reply_markup=keyboardAddress(infoUserDB, addrs, 'setNameAddr-', False), parse_mode='Markdown')


# Message for command /setaddress
@bot.message_handler(commands=['setaddress'])
def message_setname(message):
    infoUserDB = checkUser(infoUser(message))
    logger.debug("Search addresses for user: {0}".format(infoUserDB['_id']))
    addrs = addrCol.find({"idUser": infoUserDB['_id']})

    if addrs.explain()['executionStats']['nReturned'] == 0:
        logger.info("Found 0 Address User: {0}".format(infoUserDB['_id']))
        bot.send_message(chat_id=infoUserDB['_id'],
                         text=u"\u26A0 " + str(translations['noneAddr']))

    else:
        bot.send_message(chat_id=infoUserDB['_id'], text=str(translations['setcodeAddrC']),
                         reply_markup=keyboardAddress(infoUserDB, addrs, 'setCodeAddr-', False))


# Message for command /enablenotification
@bot.message_handler(commands=['enablenotification'])
def message_enablenotification(message):
    infoUserDB = checkUser(infoUser(message))
    logger.debug("Search addresses for user: {0}".format(infoUserDB['_id']))
    addrs = addrCol.find({"idUser": infoUserDB['_id']})

    if addrs.explain()['executionStats']['nReturned'] == 0:
        logger.info("Found 0 Address User: {0}".format(infoUserDB['_id']))
        bot.send_message(chat_id=infoUserDB['_id'],
                         text=u"\u26A0 " + str(translations['noneAddr']))

    else:
        bot.send_message(chat_id=infoUserDB['_id'],
                         text=str(translations['enableNotifications']),
                         reply_markup=keyboardAddress(infoUserDB, addrs, 'notON-', False), parse_mode='Markdown')


# Message for command /disablenotification
@bot.message_handler(commands=['disablenotification'])
def message_disablenotification(message):
    infoUserDB = checkUser(infoUser(message))
    logger.debug("Search addresses for user: {0}".format(infoUserDB['_id']))
    addrs = addrCol.find({"idUser": infoUserDB['_id']})

    if addrs.explain()['executionStats']['nReturned'] == 0:
        logger.info("Found 0 Address User: {0}".format(infoUserDB['_id']))
        bot.send_message(chat_id=infoUserDB['_id'],
                         text=u"\u26A0 " + str(translations['noneAddr']))

    else:
        bot.send_message(chat_id=infoUserDB['_id'],
                         text=str(translations['disableNotifications']),
                         reply_markup=keyboardAddress(infoUserDB, addrs, 'notOFF-', False), parse_mode='Markdown')


# -----------------------------

# ---------- Callbacks ----------

# Callback from inlinekeyboards
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    infoUserCall = infoUserCallback(call)

    # Send stats Pool
    if call.data == "statsp2m":
        response = requestAPI(POOLSTATS)
        logger.debug("Response API: {0}".format(response))
        convertedEpoch = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(response['stats']['lastBlockFound']))

        hashrate = str(round(response['hashrate'] / 1000000000, 2)) + " GH"
        networkDificult = str(round(int(response['nodes'][0]['difficulty']) / 1000000000000000, 3)) + " P"
        networkHashrate = str(round(int(response['nodes'][0]['lastBeat']) / 10000000, 2)) + " TH"
        messageText = u"\U0001F465 Miners Online: *{0}*\n\n".format(response['minersTotal'])
        messageText = messageText + u"\U0001F6A7 Pool Hash Rate: *{0}*\n\n".format(hashrate)
        messageText = messageText + u"\U0001F552 Last Block Found: *{0}*\n\n".format(convertedEpoch)
        messageText = messageText + u"\U0001F513 Network Difficulty: *{0}*\n\n".format(networkDificult)
        messageText = messageText + u"\u26A1 Network Hash Rate: *{0}*\n\n".format(networkHashrate)
        messageText = messageText + u"\U0001F4F6 Blockchain Height: *{0}*".format(thousandSep(response["nodes"][0]["height"]))

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messageText,
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardStats2(infoUserCall))

    # Select address for view stats
    elif call.data == "statsaddr":
        logger.debug("Search addresses for user: {0}".format(infoUserCall['_id']))
        addrs = addrCol.find({"idUser": infoUserCall['_id']})

        if addrs.explain()['executionStats']['nReturned'] == 0:
            logger.info("Found 0 Address User: {0}".format(infoUserCall['_id']))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=u"\u26A0 " + str(translations['noneAddr']))

        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=translations['selectAddr'])
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=keyboardAddress(infoUserCall, addrs, 'stats-', True))

    # Return to select address for view stats
    elif call.data == "statsReturn":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=str(translations['stats1']))
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardStats1(infoUserCall))

    # Search stats for one address
    elif re.search("^stats-+", call.data):
        addressCode = str(call.data).replace('stats-', '')
        logger.debug("Check stats for User: {0} Code Address {1}".format(infoUserCall['_id'], addressCode))
        urlStatsAddr = ADDRESSSTATS + addressCode
        responseStats = requestAPI(urlStatsAddr)
        logger.debug("Response API: {0}".format(responseStats))

        if 'ok' in responseStats and responseStats['error_code'] == 404:
            logger.info('No information for the address: {0}'.format(addressCode))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=translations['noStats'])
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=keyboardStats3(infoUserCall))
        else:
            currentHashrate = str(round(responseStats['currentHashrate'] / 1000000000, 2)) + " GH"
            hashrate = str(round(responseStats['hashrate'] / 1000000000, 2)) + " GH"

            messageText = u"\U0001F6A7  *Hashrate:*\n"
            messageText = messageText + "   - Current Hashrate (30m): *{0}*\n".format(currentHashrate)
            messageText = messageText + "   - Hashrate (3h): *{0}*\n\n".format(hashrate)

            if 'blocksFound' in responseStats['stats']:
                messageText = messageText + u"\U0001F4E6 Blocks Found: *{0}*\n\n".format(
                responseStats['stats']['blocksFound'])
            else:
                messageText = messageText + u"\U0001F4E6 Blocks Found: *0*\n\n"

            messageText = messageText + u"\U0001F4B6 *Payments:*\n"
            messageText = messageText + "   - Total Payments: *{0}*\n".format(responseStats['paymentsTotal'])

            if 'paid' in responseStats['stats']:
                messageText = messageText + "   - Total Paid: *{0}*\n\n".format(responseStats['stats']['paid'] / 1000000000)
            else:
                messageText = messageText + "   - Total Paid: *-*\n\n"
                
            messageText = messageText + u"\u2699 *Workers:*\n"
            messageText = messageText + "   - Online: *{0}*\n".format(responseStats['workersOnline'])
            messageText = messageText + "   - Offline: *{0}*\n".format(responseStats['workersOffline'])
            messageText = messageText + "   - Total: *{0}*\n".format(responseStats['workersTotal'])

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messageText,
                                  parse_mode='Markdown')
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=keyboardStats3(infoUserCall))

    # Return to keyboard myAddrs
    elif call.data == "myAddrs":
        logger.debug("Search addresses for user: {0}".format(infoUserCall['_id']))
        addrs = addrCol.find({"idUser": infoUserCall['_id']})
        logger.debug("Send keyboard myAddrs to user: {0}".format(infoUserCall['_id']))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=translations['selectAddr'],
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=infoUserCall['_id'], message_id=call.message.message_id,
                                      reply_markup=keyboardAddress(infoUserCall, addrs, 'myaddr-', False))

    # Send keyboard for edit information address
    elif re.search("^myaddr-+", call.data):
        logger.debug("Send keyboard edit information address {0}".format(infoUserCall['_id']))
        addressCode = str(call.data).replace('myaddr-', '')
        addresName = (addrCol.find_one({"address": addressCode, "idUser": infoUserCall['_id']}))['name']
        messageText = translations['viewAddr']
        messageText = messageText.replace("<NAMEADDRESS>", addresName)
        messageText = messageText.replace("<ADDRESS>", addressCode)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messageText,
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardOptionsAddr(infoUserCall, addressCode))

    # Callback to delete address
    elif re.search("^delAddr-+", call.data):
        addressCode = str(call.data).replace('delAddr-', '')
        addresName = (addrCol.find_one({"address": addressCode, "idUser": infoUserCall['_id']}))['name']
        messageText = translations['delAddr2']
        messageText = messageText.replace("<NAMEADDRESS>", addresName)
        messageText = messageText.replace("<ADDRESS>", addressCode)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messageText,
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardDeleteAddres(infoUserCall, addressCode))

    # Callback confirmed delete address
    elif re.search("^yesDelAddr-+", call.data):
        addressCode = str(call.data).replace('yesDelAddr-', '')
        logger.info("Delete addres {0} user: {1}".format(addressCode, infoUserCall['_id']))
        addrCol.delete_one({"address": addressCode, "idUser": infoUserCall['_id']})
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=translations['addrDelOk'],
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardReturnMyAddrs(infoUserCall))

    # Callback for send keyboard to edit address
    elif re.search("^editAddr-+", call.data):
        addressCode = str(call.data).replace('editAddr-', '')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=translations['optEdit'],
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardEditAddress(infoUserCall, addressCode))

    # Callback edit name for adress
    elif re.search("^setNameAddr-+", call.data):
        addressCode = str(call.data).replace('setNameAddr-', '')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=translations['newNameAddr'],
                              parse_mode='Markdown')

        logger.debug(
            "Update lastMessage.type -> setnameaddr user {0} address: {1}".format(infoUserCall['_id'], addressCode))
        userColl.update_one({"_id": str(infoUserCall['_id'])},
                            {"$set": {"lastMessage.type": "setnameaddr",
                                      "lastMessage.idMessage": str(call.message.message_id),
                                      "lastMessage.text": addressCode}})

    # Callback edit code for adress
    elif re.search("^setCodeAddr-+", call.data):
        addressCode = str(call.data).replace('setCodeAddr-', '')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=translations['newCodeAddr'],
                              parse_mode='Markdown')

        logger.debug(
            "Update lastMessage.type -> setCodeAddr user {0} address: {1}".format(infoUserCall['_id'], addressCode))
        userColl.update_one({"_id": str(infoUserCall['_id'])},
                            {"$set": {"lastMessage.type": "setcodeaddr",
                                      "lastMessage.idMessage": str(call.message.message_id),
                                      "lastMessage.text": addressCode}})

    # Callback notificatios
    elif re.search("^notAddr-+", call.data):
        addressCode = str(call.data).replace('notAddr-', '')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=translations['descNotifications'],
                              parse_mode='Markdown')

        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardNotifications(addressCode))

    # Callabck activate notifications
    elif re.search("^notON-+", call.data):
        addressCode = str(call.data).replace('notON-', '')
        logger.info("Activate notifications for: user -> {0} address ->{1}".format(infoUserCall['_id'], addressCode))
        addrCol.update_one({"address": addressCode, "idUser": infoUserCall['_id']}, {"$set": {"notifications": True}})
        messageText = translations['statusNotifications']
        messageText = messageText.replace("<STATUS>", "ON")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=messageText, parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardReturnMyAddrs(infoUserCall))

    # Callback desactivate notificationes
    elif re.search("^notOFF-+", call.data):
        addressCode = str(call.data).replace('notOFF-', '')
        logger.info("Desactivate notifications for: user -> {0} address ->{1}".format(infoUserCall['_id'], addressCode))
        addrCol.update_one({"address": addressCode, "idUser": infoUserCall['_id']}, {"$set": {"notifications": False}})
        messageText = translations['statusNotifications']
        messageText = messageText.replace("<STATUS>", "OFF")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=messageText, parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardReturnMyAddrs(infoUserCall))

    else:
        logger.warning("Unidentified callback: {0}".format(call.data))


# -------------------------------

# ---------- Others messages ----------

@bot.message_handler(func=lambda message: True)
def message_other(message):
    infoUserDB = checkUser(infoUser(message))

    # Insert name for new address
    if infoUserDB['lastMessage']['type'] == 'newaddr':
        logger.debug("Save the name address on lastMessage -> idUser: {0}, nameAddr: {1}".format(infoUserDB['_id'],
                                                                                                 message.text))
        response = bot.send_message(chat_id=infoUserDB['_id'],
                                    text=str(translations['newAddr2']),
                                    parse_mode='Markdown')
        userColl.update_one({"_id": str(infoUserDB['_id'])}, {
            "$set": {"lastMessage.type": "newaddr2", "lastMessage.idMessage": str(response.message_id),
                     "lastMessage.text": message.text}})

    # Insert new address
    elif infoUserDB['lastMessage']['type'] == 'newaddr2':
        logger.debug('Insert new address -> idUser: {0}, nameAddr: {1}, address: {2}'.format(infoUserDB['_id'],
                                                                                             infoUserDB['lastMessage'][
                                                                                                 'text'], message.text))

        addrCol.insert_one(
            {'name': infoUserDB['lastMessage']['text'], "address": message.text, "idUser": infoUserDB['_id'],
             "notifications": False, "statusWorkers": {}})

        messageText = str(translations['newAddr3'])
        messageText = messageText.replace("<NAMEADDRESS>", infoUserDB['lastMessage']['text'])
        messageText = messageText.replace("<ADDRESS>", message.text)

        bot.send_message(chat_id=infoUserDB['_id'], text=messageText, parse_mode='Markdown')
        userColl.update_one({"_id": str(infoUserDB['_id'])},
                            {"$set": {"lastMessage.type": "", "lastMessage.idMessage": "", "lastMessage.text": ""}})

    # Edit address name
    elif infoUserDB['lastMessage']['type'] == 'setnameaddr':
        logger.debug("Update the name address user: {0} address: {1} new_name: {2}".format(infoUserDB['_id'],
                                                                                           infoUserDB['lastMessage'][
                                                                                               'text'], message.text))
        addrCol.update_one({"idUser": str(infoUserDB['_id']), "address": infoUserDB['lastMessage']['text']},
                           {"$set": {"name": message.text}})
        userColl.update_one({"_id": str(infoUserDB['_id'])},
                            {"$set": {"lastMessage.type": "", "lastMessage.idMessage": "", "lastMessage.text": ""}})

        infoAddr = addrCol.find_one({'idUser': str(infoUserDB['_id']), "address": infoUserDB['lastMessage']['text']})

        messageText = str(translations['addrUpdate'])
        messageText = messageText.replace("<NAMEADDRESS>", infoAddr['name'])
        messageText = messageText.replace("<ADDRESS>", infoAddr['address'])
        bot.send_message(chat_id=infoUserDB['_id'], text=messageText, parse_mode='Markdown')

    # Edit address code
    elif infoUserDB['lastMessage']['type'] == 'setcodeaddr':
        logger.debug("Update the code address user: {0} address: {1} new_code: {2}".format(infoUserDB['_id'],
                                                                                           infoUserDB['lastMessage'][
                                                                                               'text'], message.text))
        addrCol.update_one({"idUser": str(infoUserDB['_id']), "address": infoUserDB['lastMessage']['text']},
                           {"$set": {"address": message.text}})
        userColl.update_one({"_id": str(infoUserDB['_id'])},
                            {"$set": {"lastMessage.type": "", "lastMessage.idMessage": "", "lastMessage.text": ""}})

        infoAddr = addrCol.find_one({'idUser': str(infoUserDB['_id']), "address": message.text})

        messageText = str(translations['addrUpdate'])
        messageText = messageText.replace("<NAMEADDRESS>", infoAddr['name'])
        messageText = messageText.replace("<ADDRESS>", infoAddr['address'])
        bot.send_message(chat_id=infoUserDB['_id'], text=messageText, parse_mode='Markdown')

    else:
        logger.warning("Unidentified message: {0}".format(message.text))


bot.polling(none_stop=True, timeout=123)
