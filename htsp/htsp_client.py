import threading
import logging
import sys
from utils import dict_utils
import tvheadend.htsmsg
import time
from multiprocessing import Process, Queue
from copy import copy
from Queue import Queue
from StringIO import StringIO

module_logger = logging.getLogger('htsp_client')

# Client object
# TODO merge with HTSPClient (which is currently a copy)
# Note: this class shouldn't usually be used directly, use HtspManager instead
class HTSPClient2:
    def __init__(self, addr, name = 'HTSP PyClient'):
        import htsp
        self.logger = logging.getLogger('htsp_client.HTSPClient2')
        self.client = htsp.HTSPClient(addr)
        self.seq = 1
        self.streaming_queue = Queue()
        self.rpc_queue = Queue()
        self.threaded_mode = False

    def next_sequence_number(self):
        result = self.seq
        self.seq = self.seq + 1
        return result

    def enable_threaded_mode(self, enabled=True):
        self.threaded_mode = enabled

    def send(self, func, args = {}):
        args = copy(args)
        args['method'] = func
        if self.client._user: args['username'] = self.client._user
        if self.client._pass: args['digest']   = htsmsg.hmf_bin(self.client._pass)
        serialized = htsmsg.serialize(args)
        deserialized = htsmsg.deserialize(StringIO(serialized))
        if (deserialized != args):
            raise Exception('send: message not serialized matching original message',
                            str(deserialized), str(args))

        self.logger.debug('send: ' + str(deserialized))
        self.client._sock.send(serialized)

    # Send
    def send_rpc(self, func, args = {}):
        seq = self.next_sequence_number()
        args = copy(args)
        args['seq'] = seq
        self.logger.debug("sending message: " + str(args))
        self.send(func, args)
        return seq

    # Send
    def send_streaming(self, func, args = {}):
        self.send(func, args)

    # Receive
    def recv(self):
        message = self.client.recv()
        self.logger.debug("received message: " + str(message))
        return message

    def read_next_rpc(self, seq):
        result = None
        self.logger.debug("waiting for RPC message: seq=" + str(seq))
        while (result == None):
            if ((self.threaded_mode) or (not self.rpc_queue.empty())):
                message = self.rpc_queue.get()
            else:
                message = self.recv()
            if ('seq' in message):
                if (message['seq'] == seq):
                    result = message
                else:
                    self.logger.warning("read and discarding RPC message with different sequence, expected: " + str(seq) + ", was: " + str(message['seq']) + ", message: " + str(message))
            else:
                self.logger.info("queuing streaming message: " + str(message))
                self.streaming_queue.put(message)
        self.logger.debug("received RPC message: " + str(result))
        return result

    def read_next_streaming(self):
        result = None
        self.logger.debug("waiting for streaming message")
        while (result == None):
            if (not self.streaming_queue.empty()):
                result = self.streaming_queue.get()
            else:
                message = self.recv()
                if ('seq' in message):
                    self.logger.info("queuing RPC message: " + str(message))
                    self.rpc_queue.put(message)
                else:
                    result = message
        self.logger.debug("received streaming message: " + str(result))
        return result

    def send_rpc_with_reply(self, func, args = {}):
        seq = self.send_rpc(func, args)
        return self.read_next_rpc(seq)

    def hello(self):
        return self.client.hello()

    def authenticate(self, user, passwd = None):
        return self.client.authenticate(user, passwd)

    def get_disk_space(self):
        args = {}
        return self.send_rpc_with_reply('getDiskSpace', args)

    def get_sys_time(self):
        args = {}
        return self.send_rpc_with_reply('getSysTime', args)

    def enable_async_metadata(self):
        args = {}
        return self.send_rpc_with_reply('enableAsyncMetadata', args)

    def add_dvr_entry(self, dvr_entry):
        return self.send_rpc_with_reply('addDvrEntry', dvr_entry)

    def remove_dvr_entry(self, id):
        args = {'id': id}
        return self.send_rpc_with_reply('deleteDvrEntry', args)

    def is_error(self, message):
        return ('error' in message)

    def is_success(self, message):
        return not self.is_error(message)

class HtspManager:

    def __init__(self, addr, user = None, passwd = None, name = 'HTSP PyClient'):
        self.logger = logging.getLogger('htsp_client.HtspManager')
        self.user = user
        self.passwd = passwd
        self.tags = []
        self.channels = []
        self.dvr_entries = []
        self.initial_sync_completed = False
        self.client = self.connect(addr, name)

    def connect(self, addr, name):
        lastException = None
        maxAttempts = 100
        delayBetweenAttempts = 10
        self.logger.info("waiting to connect: " + str(addr) + ", name: " + name)
        for attempt in range(maxAttempts):
            try:
                return HTSPClient2(addr, name)
            except Exception as exc:
                lastException = exc
                if (attempt < maxAttempts):
                    self.logger.debug("failed to connect: " + str(addr) + ", name: " + name + ", error: " + str(lastException) + ", attempt: " + str(1 + attempt))
                    time.sleep(delayBetweenAttempts)
        self.logger.error("failed to connect: " + str(addr) + ", name: " + name + ", error: " + str(lastException))
        e = Exception("failed to connect to " + str(addr))
        e.__cause__ = lastException
        raise e

    def index_by(self, list, key, value):
        index = None
        for i in range(len(list)):
            entry = list[i]
            if (entry[key] == value):
                index = i
                break
        return index

    def find_by_and_get_value(self, list, key, value, key_value):
        index = self.index_by(list, key, value)
        return list[index][key_value] if index != None else None

    def channel_id_by_name(self, channel_name):
        return self.find_by_and_get_value(self.channels, 'name', channel_name, 'id')

    def to_date_time(self, x):
        return x

    def to_string(self, x):
        return x

    def init(self):
        client = self.client
        response = client.hello()
        self.logger.info("hello response:" + str(response))
        client.authenticate(self.user, self.passwd)
        self.logger.info("disk space:" + str(client.get_disk_space()))
        self.logger.info("sys time:" + str(client.get_sys_time()))
        self.logger.info("enable_async_metadata:" + str(client.enable_async_metadata()))
        while not self.initial_sync_completed:
            message = self.client.read_next_streaming()
            self.logger.debug("next:" + str(message))
            self.process_streaming_message(message)

    def error_message(self, error):
        return {'error': error}

    def index_of_exisiting_dvr_entry(self, channel_id, start):
        result = None
        for i in range(len(self.dvr_entries)):
            entry = self.dvr_entries[i]
            if (('channelId' in entry) and (entry['channelId'] == channel_id) and
                    ('start' in entry) and (entry['start'] == start)):
                result = i
                break
        return result

    def dvr_entry_id_by_channel_id_and_start(self, channel_id, start):
        index = self.index_of_exisiting_dvr_entry(channel_id, start)
        return self.dvr_entries[index]['id'] if (index != None) else None

    def add_dvr_entry(self, dvr_entry):
        entry = {}
        if ('channelId' in dvr_entry):
            entry['channelId'] = int(dvr_entry['channelId'])
        elif ('channel' in dvr_entry):
            channel_name = dvr_entry['channel']
            channel_id = self.channel_id_by_name(channel_name)
            if (channel_id == None):
                return self.error_message('invalid channel: ' + channel_name)
            entry['channelId'] = channel_id
        else:
            return self.error_message('channel missing')
        if ('start' in dvr_entry):
            entry['start'] = int(self.to_date_time(dvr_entry['start']))
        else:
            return self.error_message('start missing')
        if ('stop' in dvr_entry):
            entry['stop'] = int(self.to_date_time(dvr_entry['stop']))
        else:
            return self.error_message('stop missing')
        if ('title' in dvr_entry):
            entry['title'] = self.to_string(dvr_entry['title'])
        else:
            return self.error_message('title missing')
        if ('configName' in dvr_entry):
            entry['configName'] = self.to_string(dvr_entry['configName'])
        index = self.index_of_exisiting_dvr_entry(entry['channelId'], entry['start'])
        if (index != None):
            return self.error_message('another DVR recording for the same channel and start time already exists')
        return self.client.add_dvr_entry(entry)

    def remove_dvr_entry(self, dvr_entry):
        channel_id = None
        if ('channelId' in dvr_entry):
            channel_id = int(dvr_entry['channelId'])
        elif ('channel' in dvr_entry):
            channel_name = dvr_entry['channel']
            channel_id = self.channel_id_by_name(channel_name)
            if (channel_id == None):
                return self.error_message('invalid channel: ' + channel_name)
        else:
            return self.error_message('channel missing')
        start = None
        if ('start' in dvr_entry):
            start = long(self.to_date_time(dvr_entry['start']))
        else:
            return self.error_message('start missing')
        dvr_entry_id = self.dvr_entry_id_by_channel_id_and_start(channel_id, start)
        if (dvr_entry_id == None):
            return self.error_message('DVR recording not found')
        else:
            return self.client.remove_dvr_entry(dvr_entry_id)

    def start(self):
        t = threading.Thread(target=self.run, args = (1, ))
        #t.daemon = True
        t.start()

    def message_to_channel(self, message, original=None):
        return dict_utils.merge(original, dict_utils.extract_and_map_keys(message,
            {'channelId': 'id', 'channelName': 'name', 'tags': 'tags'}))

    def message_to_tag(self, message, original=None):
        return dict_utils.merge(original, dict_utils.extract_and_map_keys(message,
            {'tagId': 'id', 'tagName': 'name'}))

    def message_to_dvr_entry(self, message, original=None):
        return dict_utils.merge(original, dict_utils.extract_and_map_keys(message,
            {'id': 'id', 'channel': 'channelId', 'start': 'start', 'stop': 'stop', 'title': 'title', 'state': 'state', 'description': 'description',
             'configName': 'configName'}))

    def process_streaming_message(self, message):
        try:
            if ('method' in message):
                method = message['method']
                if (method == 'channelAdd'):
                    channel = self.message_to_channel(message)
                    self.channels.append(channel)
                    if (self.initial_sync_completed):
                        self.logger.info("added channel: " + str(channel.get('id')) + ", name: " + str(channel.get('channelName')) + ", count: " + str(len(self.channels)))
                elif (method == 'channelUpdate'):
                    index = self.index_by(self.channels, 'id', message['channelId'])
                    if (index != None):
                        channel = self.message_to_channel(message, self.channels[index])
                        self.channels[index] = channel
                        self.logger.info("updated channel: " + str(channel.get('id')) + ", name: " + str(channel.get('channelName')))
                    else:
                        self.logger.warning("channel not found: " + str(message['channelId']))
                elif (method == 'channelDelete'):
                    index = self.index_by(self.channels, 'id', message['channelId'])
                    if (index != None):
                        channel = self.channels[index]
                        del self.channels[index]
                        self.logger.info("deleted channel: " + str(channel.get('id')) + ", name: " + str(channel.get('name')) + ", remaining: " + str(len(self.channels)))
                    else:
                        self.logger.warning("channel not found: " + str(message['channelId']))
                elif (method == 'tagAdd'):
                    self.tags.append(self.message_to_tag(message))
                    if (self.initial_sync_completed):
                        self.logger.info("added tag: " + str(message['tagId']) + ", name: " + str(message['tagName']) + ", count: " + str(len(self.tags)))
                elif (method == 'tagUpdate'):
                    index = self.index_by(self.tags, 'id', message['tagId'])
                    if (index != None):
                        self.tags[index] = self.message_to_tag(message, self.tags[index])
                        self.logger.info("updated tag: " + str(message['tagId']) + ", name: " + str(message['tagName']))
                    else:
                        self.logger.warning("tag not found: " + str(message['tagId']))
                elif (method == 'tagDelete'):
                    index = self.index_by(self.tags, 'id', message['tagId'])
                    if (index != None):
                        tag = self.tags[index]
                        del self.tags[index]
                        self.logger.info("deleted tag: " + str(message['tagId']) + ", name: " + str(tag['name']) + ", remaining: " + str(len(self.tags)))
                    else:
                        self.logger.warning("channel not found: " + str(message['channelId']))
                elif (method == 'dvrEntryAdd'):
                    self.dvr_entries.append(self.message_to_dvr_entry(message))
                    if (self.initial_sync_completed):
                        self.logger.info("added DVR entry: " + str(message['id']) + ", count: " + str(len(self.dvr_entries)))
                elif (method == 'dvrEntryUpdate'):
                    index = self.index_by(self.tags, 'id', message['id'])
                    if (index != None):
                        self.dvr_entries[index] = self.message_to_dvr_entry(message, self.dvr_entries[index])
                        self.logger.info("updated DVR entry: " + str(message['id']) + ", name: " + str(message))
                    else:
                        self.logger.warning("DVR entry not found: " + str(message['id']))
                elif (method == 'dvrEntryDelete'):
                    index = self.index_by(self.dvr_entries, 'id', message['id'])
                    if (index != None):
                        del self.dvr_entries[index]
                        self.logger.info("deleted DVR entry: " + str(message['id']) + ", remaining: " + str(len(self.dvr_entries)))
                    else:
                        self.logger.warning("DVR entry not found: " + str(message['id']))
                elif (method == 'initialSyncCompleted'):
                    self.initial_sync_completed = True
                    self.logger.info("tags: " + str(self.tags))
                    self.logger.info("channels: " + str(len(self.channels)))
                    self.logger.info("dvr_entries: " + str(len(self.dvr_entries)))
                else:
                    self.logger.info("ignoring unrecognised method: " + str(method))
            elif ('error' in message):
                error = message['error']
                self.logger.error("some error happened: " + str(error))
            else:
                self.logger.error("invalid message: " + str(message))
        except:
            self.logger.error("failed to process message: " + str(message) + ", error: " + str(sys.exc_info()[0]))
            raise

    def run(self, arg = None):
        self.logger.debug("entering thread, arg: " + str(arg))
        self.client.enable_threaded_mode(True)
        try:
            while True:
                message = self.client.read_next_streaming()
                self.logger.debug("next:" + str(message))
                self.process_streaming_message(message)
        finally:
            self.client.enable_threaded_mode(False)
            self.logger.info("exiting thread")

    def is_error(self, message):
        return self.client.is_error(message)

    def is_bad_request(self, message):
        return self.is_error(message) and (not 'seq' in message)

    def is_success(self, message):
        return self.client.is_success(message)
