import json
import logging
import urllib.request
import os

print('Loading function... ')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def event_to_json(event):
    if 'body' in event:
        body = json.loads(event.get('body'))
        return body
    elif 'token' in event:
        body = event
        return body
    else:
        logger.error('unexpected event format')
        exit


class ChallangeJson(object):
    def data(self, key):
        return {
            'isBase64Encoded': 'true',
            'statusCode': 200,
            'headers': {},
            'body': key
        }


class PostJson(object):
    def __init__(self):
        #self.BOT_TOKEN = os.environ['BOT_TOKEN']
        #self.OAUTH_TOKEN = os.environ['OAUTH_TOKEN']
        #self.BOT_NAME = os.environ['BOT_NAME']
        #self.BOT_ICON = os.environ['BOT_ICON']
        self.LEGACY_TOKEN = os.environ['LEGACY_TOKEN']

    def headers(self):
        return {
            'Content-Type': 'application/json; charset=UTF-8',
            'Authorization': 'Bearer {0}'.format(self.LEGACY_TOKEN)
        }

    def invite(self, channel, user):
        return {
            'token': self.LEGACY_TOKEN,
            'channel': channel,
            'user': user
        }


def handler(event, context):
    TARGET_CHANNELS = os.environ['TARGET_CHANNELS']
    #REPLY_DATA = os.environ['REPLY_DATA']
    #OAUTH_TOKEN = os.environ['OAUTH_TOKEN']

    # Output the received event to the log
    # logging.info(json.dumps(event))
    body = event_to_json(event)

    # return if it was challange-event
    if 'challenge' in body:
        challenge_key = body.get('challenge')
        logging.info('return challenge key %s:', challenge_key)
        return ChallangeJson().data(challenge_key)

    # Hook Leave event and specific Channel
    target_channels = TARGET_CHANNELS.split(',')
    if body.get('event').get('channel', '') in target_channels and body.get('event').get('subtype', '') == 'channel_leave':
        logger.info('hit: %s', TARGET_CHANNELS)
        post_head = PostJson().headers()

        # invite user
        channel_invite = body.get('event').get('channel', '')
        user_invite = body.get('event').get('user', '')
        post_data = PostJson().invite(channel_invite,user_invite)
        # POST
        url = 'https://slack.com/api/channels.invite'
        req = urllib.request.Request(
            url,
            data=json.dumps(post_data).encode('utf-8'),
            method='POST',
            headers=post_head)
        res = urllib.request.urlopen(req)
        tmp = json.loads(res.read().decode('utf8')) #dbg
        logger.info('dbg: %s', tmp) #dbg
        #logger.info('post result: %s', res.msg)

    return {'statusCode': 200, 'body': 'ok'}
