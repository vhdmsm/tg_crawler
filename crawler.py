# -*- coding: utf-8 -*-

import sqlite3, time
from datetime import datetime
from channel_finder import *
from pytg import *

__author__ = 'Vahid Masoumi'


def create_db(conn, c):
    c.execute('''CREATE TABLE if not exists ChannelMessages
               (channel_name blob, participants_count blob, admins_count blob, message blob, date_of_message text,
                message_type text, sender_type text,
                fwd_from_full_name text, fwd_from_peer_type text, fwd_from_username text, fwd_from_peer_id text, channel_id blob,
                PRIMARY KEY (channel_name, message))''')

    c.execute('''CREATE TABLE if not exists GroupMessages
             (group_name blob, group_id blob, sender_firstname blob, sender_lastname blob, sender_username text, sender_id text, reply_id text, message_type text, message blob, sender_type text, date_of_message text, group_members_count text, fwd_from_full_name text, fwd_from_peer_type text, fwd_from_username text, fwd_from_peer_id text, service text, user_action text, useraction_firstname blob, useraction_lastname blob, useraction_username text, useraction_id text,
             PRIMARY KEY (group_id, message, date_of_message))''')

    c.execute('''CREATE TABLE if not exists SupergroupMessages
             (supergroup_name blob, members_num blob, admins_count blob, supergroup_id blob, sender_firstname blob, sender_lastname blob, sender_username text, sender_id text, reply_id text, message_type text, message blob, sender_type text, date_of_message text, fwd_from_full_name text, fwd_from_peer_type text, fwd_from_username text, fwd_from_peer_id text, service text, user_action text, useraction_firstname blob, useraction_lastname blob, useraction_username text, useraction_id text,
             PRIMARY KEY (supergroup_id, message, date_of_message))''')
    conn.commit()


def write_in_file(file_name, row=None):
    print("++++++ write in file\n")
    output = codecs.open('%s.txt' % file_name, 'a', 'utf-8')
    output.write(row)


def check_in_file(file_name, row=None):
    print("++++++ check in file\n")
    output = codecs.open('%s.txt' % file_name, 'r', 'utf-8')
    if row in output.read():
        return True
    return False


def get_channel_list():
    file_name = "channels_list"
    output = codecs.open('%s.txt' % file_name, 'r', 'utf-8')
    return [line.replace("\n", "") for line in output.readlines()]


def get_channel_data(conn,c, sender, channel_list, channels_number, new_channel_messages_number, dumping_time, is_manual):
    for channel in channel_list:
        try:
            ch_info = sender.channel_info(channel.id if not is_manual else channel)
            print(ch_info)
            channels_number += 1
            print("time: %s #channel: %d, channel_id: %s\n" % (time.ctime(), channels_number, channel.id if not is_manual else channel))
            messages = sender.history(channel.id if not is_manual else channel, 400)
            print("length of channel messages: %d" % len(messages))

            dumping_time = datetime.now() - dumping_time

            msg_count = 0
            for msg in messages:
                if msg.get('event', '') == 'message':
                    if msg.get('from', '').get('peer_type', '') == "channel":  # it's channel
                        if msg_count == 99:
                            print(msg)
                        if insert_to_channel_table(msg, ch_info, conn, c, sender=sender):
                            new_channel_messages_number += 1
                    elif msg.get('from', '').get('peer_type', '') == "chat":  # it's group
                        # print("Message Type: Group\n")
                        pass
                    elif msg.get('from', '').get('peer_type', '') == "user":  # it's private message
                        handle_private_messages(msg, ch_info, conn, c, sender=sender)
                        print("Private message: %s" % msg)
                    else:
                        print("Not a channel, group or user message\n")
                        print(msg)

                msg_count += 1
        except Exception as err:  # from pytg.exceptions import NoResponse
            print("in channel %s error has been occurred!" % (channel.id if not is_manual else channel))

    return channel_list, channels_number, new_channel_messages_number, dumping_time


def process_channels(conn, c, sender):
    dumping_time = datetime.now()
    print("Channel Dumper is running at %s\n" % time.ctime())
    channels_number, new_channel_messages_number, new_group_messages_number = 0, 0, 0
    print("getting channel list from tg...")
    # channel_list = sender.channel_list(100)
    manual_channel_list = get_channel_list()
    channel_list, channels_number, new_channel_messages_number, dumping_time = get_channel_data(conn,c, sender, manual_channel_list, channels_number, new_channel_messages_number, dumping_time, True)

    dumping_time = datetime.now() - dumping_time
    print("\n++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("DONE! All of the messages are saved successfully!")
    print("Dumping time: %s" % dumping_time)
    print("Total number of channels: %d" % channels_number)
    print("Total number of new channel messages: %d" % new_channel_messages_number)
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")


def processor(conn, c, sender):
    dumping_time = datetime.now()
    print("Telegram Dumper is running at %s\n" % time.ctime())
    process_channels(conn, c, sender)
    channels_number, groups_number, new_channel_messages_number, new_group_messages_number = 0, 0, 0, 0
    dialog_list = sender.dialog_list(1000)

    for item in dialog_list:
        if item.get('peer_type', '') == 'channel':
            channels_number += 1
            new_channel_messages_number += process_channel(conn, c, sender, item, channels_number)
        elif item.get('peer_type', '') == 'chat':
            groups_number += 1
            new_group_messages_number += process_group(conn, c, sender, item, groups_number)
        else:
            print("it's not group nor channel")
            continue

    dumping_time = datetime.now() - dumping_time
    print("\n++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("DONE! All of the messages are saved successfully!")
    print("Dumping time: %s" % dumping_time)
    print("Total number of channels: %d" % channels_number)
    print("Total number of groups: %d" % groups_number)
    print("Total number of new channel messages: %d" % new_channel_messages_number)
    print("Total number of new group messages: %d" % new_group_messages_number)
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")


def process_group(conn, c, sender, group, groups_number):
    new_msg_count = 0
    try:
        print("time: %s #group: %d, group_id: %s\n" % (time.ctime(), groups_number, group.id))
        messages = sender.history(group.id, 5000)
        print("Length of group messages: %d" % len(messages))
        for msg in messages:
            if msg.get('event', '') == 'message' or msg.get('event', '') == 'service':
                print(msg)
                if insert_to_group_table(msg, conn, c, sender):
                    new_msg_count += 1
            else:
                print(msg)

    except Exception as err:  # from pytg.exceptions import NoResponse
        print("in group %s error has been occurred!: %s" % (group.id, err))
        import traceback
        print(traceback.format_exc())
    return new_msg_count


def process_channel(conn, c, sender, channel, channels_number):
    new_msg_count = 0
    try:
        ch_info = sender.channel_info(channel.id)
        messages = sender.history(channel.id, 400)
        print("Length of channel messages: %d" % len(messages))
        for msg in messages:
            if msg.get('event', '') == 'message':
                if msg.get('from', '').get('peer_type', '') == "channel":  # it's channel
                    print("time: %s #channel: %d, channel_id: %s\n" % (time.ctime(), channels_number, channel.id))
                    if insert_to_channel_table(msg, ch_info, conn, c, sender=sender):
                        new_msg_count += 1
                elif msg.get('from', '').get('peer_type', '') == "user":  # it's supergroup
                    print("******* SUPERGROUP *******")
                    print("time: %s #supergroup: %d, supergroup_id: %s\n" % (time.ctime(), channels_number, channel.id))
                    if insert_to_supergroup_table(msg, ch_info, conn, c, sender):
                        new_msg_count += 1

    except Exception as err:  # from pytg.exceptions import NoResponse
        print("in channel %s error has been occurred!: %s" % (channel.id, err))
        import traceback
        print(traceback.format_exc())
    return new_msg_count


def handle_private_messages(msg, ch_info, conn, c, sender):
    pass


def insert_to_channel_table(msg, ch_info, conn, c, sender):
    new_one = True
    message_or_caption = msg.get('text', '').replace("\n", " ").replace("'", "") if msg.get('text', '').replace("\n",
                                                                                                                " ") else msg.get(
            'media', '').get('caption', '').replace("\n", " ").replace("'", "")

    original_message_or_caption = msg.get('text', '').replace("'", "") if msg.get('text', '') else (msg.get('media', '').get('caption', '').replace("\n", " ").replace("'", "") if msg.get('media', '') else '')
    find_channel_and_join(original_message_or_caption, sender)

    if msg.get('fwd_from', ''):
        insert_cmd = "'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s', '%s', '%s', '%s', '%s'" % (
            msg.to.get('title', ''), ch_info.participants_count, ch_info.admins_count, message_or_caption, msg.date,
            'Text' if msg.get('text', '').replace("\n", " ") else 'Media', msg.get('from', '').get('first_name'),
            msg.get('from', '').get('last_name'), msg.get('from', '').peer_type,
            msg.fwd_from.get('print_name'), msg.fwd_from.peer_type, msg.fwd_from.get('username', ''),
            msg.fwd_from.peer_id, ch_info.id)
    else:
        insert_cmd = "'%s', '%s', '%s', '%s','%s', '%s', '%s', '%s', '%s','%s', '%s', '%s', '%s', '%s'" % (
            msg.to.get('title', ''), ch_info.participants_count, ch_info.admins_count, message_or_caption, msg.date,
            'Text' if msg.get('text', '').replace("\n", " ") else 'Media', msg.get('from', '').get('first_name'),
            msg.get('from', '').get('last_name'), msg.get('from', '').peer_type,
            '', '', '', '', ch_info.id)
    try:
        c.execute("INSERT INTO ChannelMessages VALUES (%s)" % insert_cmd)
        write_in_file("ChannelMessages", "%s\n" % insert_cmd)
        print("++++++ Inserted to channel table\n")
        conn.commit()
    except Exception as err:
        new_one = False
    return new_one


def insert_to_supergroup_table(msg, ch_info, conn, c, sender):
    new_one = True
    print(">>>> Called insert to supergroup table\n")
    print(msg)

    message_or_caption = msg.get('text', '').replace("\n", " ") if msg.get('text', '').replace("\n"," ") else\
        (msg.get('media', '').get('caption', '').replace("\n", " ").replace("'", "") if msg.get('media', '') else '')

    original_message_or_caption = msg.get('text', '').replace("'", "") if msg.get('text', '') else (msg.get('media', '').get('caption', '').replace("\n", " ").replace("'", "") if msg.get('media', '') else '')
    # find_groups_and_join(original_message_or_caption, sender)

    action_user = {}
    if msg.get('action', ''):
        if msg.get('action', '').get('user', ''):
            action_user = msg.get('action', '').get('user', '')

    if msg.get('fwd_from', ''):
        insert_cmd = "'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s'" % (
            ch_info.title, ch_info.participants_count, ch_info.admins_count,
            ch_info.id, msg.get('from', '').get('first_name', ''),
            msg.get('from', '').get('last_name', ''),
            msg.get('from', '').get('username', ''), msg.get('from', '').peer_id, msg.get('reply_id', ''),
            'Text' if msg.get('text', '').replace("\n", " ") else 'Media', message_or_caption,
            msg.get('from', '').get('peer_type', ''), msg.date,
            msg.fwd_from.get('print_name'), msg.fwd_from.peer_type, msg.fwd_from.get('username', ''),msg.fwd_from.peer_id,
            msg.get('service', 'False'),
            msg.get('action', '').get('type', '') if msg.get('action', '') else '',
            action_user.get('first_name', ''),
            action_user.get('last_name', ''),
            action_user.get('username', ''),
            action_user.get('id', '')
        )
    else:
        insert_cmd = "'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s'" % (
            ch_info.title, ch_info.participants_count, ch_info.admins_count,
            ch_info.id, msg.get('from', '').get('first_name', ''),
            msg.get('from', '').get('last_name', ''),
            msg.get('from', '').get('username', ''), msg.get('from', '').peer_id, msg.get('reply_id', ''),
            'Text' if msg.get('text', '').replace("\n", " ") else 'Media', message_or_caption,
            msg.get('from', '').get('peer_type', ''), msg.date,
            '', '', '', '',
            msg.get('service', 'False'),
            msg.get('action', '').get('type', '') if msg.get('action', '') else '',
            action_user.get('first_name', ''),
            action_user.get('last_name', ''),
            action_user.get('username', ''),
            action_user.get('id', '')
        )
    try:
        c.execute("INSERT INTO SupergroupMessages VALUES (" + insert_cmd + ")")
        write_in_file("SupergroupMessages", "%s\n" % insert_cmd)
        print("+++++++ Inserted to Supergroup table\n")
        conn.commit()
    except Exception as err:
        new_one = False
        print("in supergroup %s error has been occurred!: %s" % (ch_info.id, err))
        import traceback
        print(traceback.format_exc())
    return new_one


def insert_to_group_table(msg, conn, c, sender):
    new_one = True
    print(">>>> Called insert to group table\n")
    print(msg)

    message_or_caption = msg.get('text', '').replace("\n", " ") if msg.get('text', '').replace("\n"," ") else\
        (msg.get('media', '').get('caption', '').replace("\n", " ").replace("'", "") if msg.get('media', '') else '')

    original_message_or_caption = msg.get('text', '').replace("'", "") if msg.get('text', '') else (msg.get('media', '').get('caption', '').replace("\n", " ").replace("'", "") if msg.get('media', '') else '')
    # find_groups_and_join(original_message_or_caption, sender)

    action_user = {}
    if msg.get('action', ''):
        if msg.get('action', '').get('user', ''):
            action_user = msg.get('action', '').get('user', '')

    if msg.get('fwd_from', ''):
        insert_cmd = "'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s'" % (
            msg.get('to', '').get('title', ''), msg.get('to', '').get('id', ''), msg.get('from', '').get('first_name', ''),
            msg.get('from', '').get('last_name', ''),
            msg.get('from', '').get('username', ''), msg.get('from', '').peer_id, msg.get('reply_id', ''),
            'Text' if msg.get('text', '').replace("\n", " ") else 'Media', message_or_caption,
            msg.get('from', '').get('peer_type', ''),
            msg.date, msg.get('to', '').members_num,
            msg.fwd_from.get('print_name'), msg.fwd_from.peer_type, msg.fwd_from.get('username', ''),
            msg.fwd_from.peer_id,
            msg.get('service', 'False'),
            msg.get('action', '').get('type', '') if msg.get('action', '') else '',
            action_user.get('first_name', ''),
            action_user.get('last_name', ''),
            action_user.get('username', ''),
            action_user.get('id', '')
        )
    else:
        insert_cmd = "'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s'" % (
            msg.get('to', '').get('title', ''), msg.get('to', '').get('id', ''), msg.get('from', '').get('first_name', ''),
            msg.get('from', '').get('last_name', ''),
            msg.get('from', '').get('username', ''),
            msg.get('from', '').peer_id, msg.get('reply_id', ''),
            'Text' if msg.get('text', '').replace("\n", " ") else 'Media', message_or_caption,
            msg.get('from', '').get('peer_type', ''),
            msg.date, msg.get('to', '').get('members_num', ''),
            '', '', '', '',
            msg.get('service', 'False'),
            msg.get('action', '').get('type', '') if msg.get('action', '') else '',
            action_user.get('first_name', ''),
            action_user.get('last_name', ''),
            action_user.get('username', ''),
            action_user.get('id', '')
        )
    try:
        c.execute("INSERT INTO GroupMessages VALUES (" + insert_cmd + ")")
        write_in_file("GroupMessages", "%s\n" % insert_cmd)
        print("+++++++ Inserted to Group table\n")
        conn.commit()
    except Exception as err:
        new_one = False
    return new_one


if __name__ == '__main__':
    print("Running crawler...")
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    create_db(conn, c)
    tg = Telegram(
            telegram="/path/to/tg/bin/telegram-cli", # for example: "/Users/vahid/PycharmProjects/tchannels-gif/tg/bin/telegram-cli"
            pubkey_file="/path/to/tg/tg-server.pub") # for example: "/Users/vahid/PycharmProjects/tchannels-gif/tg/server.pub"
    receiver = tg.receiver
    sender = tg.sender
    # sender = Sender("127.0.0.1", 4458)
    sender.default_answer_timeout = 50
    processor(conn, c, sender)
