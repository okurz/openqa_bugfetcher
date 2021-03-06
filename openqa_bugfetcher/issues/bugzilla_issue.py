#!/usr/bin/python3

from openqa_bugfetcher.issues import BaseIssue
from collections import OrderedDict
import requests
import json

class BugzillaIssue(BaseIssue):
    prefixes = {'boo', 'bnc', 'bsc'}

    def fetch(self, conf):
        def json_rpc_get(url, method, params):
            get_params = OrderedDict({'method': method, 'params': json.dumps([params])})
            a = conf['bugzilla']
            return requests.get(url, params=get_params, auth=(a['user'], a['pass']))
        url = 'https://apibugzilla.suse.com/jsonrpc.cgi'

        issue_id = self.bugid.split('#')[1]
        r = json_rpc_get(url, 'Bug.get', {"ids": [issue_id]})
        assert r.status_code != 401, "Wrong auth for Bugzilla"
        assert r.ok
        j = r.json()
        if j['error'] and j['error']['code'] == 101:
            self.existing = False
        else:
            b = j['result']['bugs'][0]
            self.title = b['summary']
            self.priority = b['priority']
            self.assignee = b['assigned_to']
            self.assigned = not self.assignee.endswith('@forge.provo.novell.com')
            self.open = b['is_open']
            self.status = b['status']
            self.resolution = b.get('resolution')
