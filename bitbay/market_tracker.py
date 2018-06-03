
import sys
import os
import inspect
import re
import time
import errno
import ast
import json

from datetime import date, datetime, timedelta
import mysql.connector

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + '/../src')

import traceback

if __name__ == '__main__':
    import appdirs
    datadir_path = appdirs.user_data_dir("MarketTracker", "BitBay")
    print "Data path:", datadir_path

    try:
        os.makedirs(datadir_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(datadir_path):
            pass
        else:
            raise

    mysql_user = 'bitbay'
    mysql_pass = '7D2NE3h0J1A'
    mysql_db = 'bitbay_market_tracker'

    cnx = mysql.connector.connect(
        user=mysql_user, password=mysql_pass, database=mysql_db)
    cursor = cnx.cursor()

    os.environ['no_proxy'] = '127.0.0.1,localhost'
    os.environ["BITMESSAGE_HOME"] = datadir_path

    import class_api as class_api
    api = class_api.getAPI(silent=True)

    import logging
    logger = logging.getLogger('class_api')

    try:
        secs = 0
        while True:
            time.sleep(1)
            secs = secs + 1
            try:
                logger.warning("Checking inbox...")
                msgs = api.getAllInboxUnreadMessages()
                logger.warning(json.dumps(msgs))

                for msg in msgs:
                    ins_msg = ("INSERT INTO bm_inbox "
                               "(msgid, receivedTime, encodingType, toAddress, fromAddress, subject, message) "
                               "VALUES (%(msgid)s, %(receivedTime)s, %(encodingType)s, %(toAddress)s, %(fromAddress)s, %(subject)s, %(message_json)s)")

                    msg_json = ""
                    try:
                        msg_data = ast.literal_eval(msg["message"])
                        msg_json = json.dumps(msg_data)
                    except:
                        pass
                    msg["message_json"] = msg_json
                    cursor.execute(ins_msg, msg)
                    cnx.commit()

                    api.markInboxMessageAsRead(msg["msgid"])

            except:
                traceback.print_exc()
                logger.error("Checking/Thread Error")

            if secs > (15 * 60):
                secs = 0
                try:
                    cursor.close()
                    cnx.close()
                except:
                    traceback.print_exc()
                    logger.error("Can not close cursor/connection")

                cnx = mysql.connector.connect(
                    user=mysql_user, password=mysql_pass, database=mysql_db)
                cursor = cnx.cursor()

    except KeyboardInterrupt:
        logger.warning("Closing market tracker...")
        sys.exit()
