__author__ = 'sunary'


import time
from datetime import datetime, timedelta
from utils.my_mongo import Mongodb


class KeyManager():

    HEARTBEAT_TIME = 10
    SCREEN_TIME = 15 * 60

    def __init__(self):
        self.mongo = Mongodb()

    def get(self, group=None):
        spec = {}
        if group:
            spec['group'] = group

        while True:
            spec['available_in'] = {'$lt': datetime.utcnow()}

            one_key = self.mongo.find_one(spec)
            if one_key:
                self.heartbeat(one_key['_id'])
                return one_key
            else:
                time.sleep(self.HEARTBEAT_TIME)

    def heartbeat(self, id, delay=None):
        if delay is None:
            delay = self.HEARTBEAT_TIME
        self.mongo.update({'_id': id}, {'available_in': datetime.utcnow() + timedelta(seconds=self.SCREEN_TIME + delay),
                                        'updated_at': datetime.utcnow()})

    def release(self, id):
        self.heartbeat(id, delay=1)

    def report(self, id, message=None):
        doc = self.mongo.find_one({'_id': id}, ['group'])

        report_group = doc['group'] + '-report'
        update_doc = {'group': report_group,
                      'updated_at': datetime.utcnow()}

        if message:
            update_doc['message'] = message

        return self.mongo.update({'_id': id}, update_doc)

    def unreport(self, group=None, id=None):
        update_doc = {'updated_at': datetime.utcnow()}
        if group:
            update_doc.update({'group': group})
            return self.mongo.update({'group': group + '-report'}, update_doc)
        elif id:
            update_doc.update({'group': group})
            return self.mongo.update({'_id': id}, update_doc)

        return None

    def add(self, key, group):
        key['group'] = group
        key['available_in'] = datetime.utcnow()
        key['created_at'] = datetime.utcnow()
        self.mongo.insert(key)

    def remove(self, id):
        self.mongo.remove({'_id': id})


if __name__ == '__main__':
    pass