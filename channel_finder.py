import codecs


def end_of_username_character(char):
    if char == ' ' or char == '\t' or char == '\n':
        return True
    return False


def extract_channel_username(msg):
    channel_username = ""
    if msg.find('@') != -1:
        channel_username += "@"
        start_index = msg.find('@') + 1
        import re
        for char in msg[start_index:]:
            if end_of_username_character(char):
                return channel_username
            if re.match('[a-zA-Z0-9_]', char):
                channel_username += char
            else:
                return channel_username
        # print("Channel Found: %s \n" % channel_username)
    return channel_username


def update_channel_list(channel_username):
    file_name = "channel_username_list"
    output = codecs.open('%s.txt' % file_name, 'a', 'utf-8')
    output.write("%s\n" % channel_username)


def check_new_channel(channel_username):
    file_name = "channel_username_list"
    output = codecs.open('%s.txt' % file_name, 'r', 'utf-8')
    output_lines = output.read()
    if output_lines.find(channel_username) != -1:
        return False
    update_channel_list(channel_username)
    return True


def find_channel_and_join(msg, sender):
    channel_username = extract_channel_username(msg)

    if check_new_channel(channel_username):
        try:
            sender.channel_join(channel_username)
            print("Joined in channel %s" % channel_username)
        except Exception as err:
            print("channel exists...")

