import json
import urllib2
import os
import yaml

try:
    with open('%s%sconfig.yml' % (os.path.dirname(os.path.realpath( __file__ )), os.sep)) as f:
        CONFIG = yaml.load(f)
except IOError:
    print 'Configuration file (config.yml) is missing. Please make one.'
    exit()
except:
    raise

API_TOKEN = CONFIG.get('telegram_token', False)
assert API_TOKEN, 'Telegram api token not found.'

BASE_URL = 'https://api.telegram.org/bot%s' % (API_TOKEN)

def json_request(method, payload):
    url = '%s/%s' % (BASE_URL, method)
    payload_text = json.dumps(payload)

    request = urllib2.Request(url, payload_text)
    request.add_header('Content-Type', 'application/json')
    result = False
    try:
        res = urllib2.urlopen(request)
        body = res.read()
        result = json.loads(body)
    except KeyboardInterrupt:
        raise
    except:
        pass

    return result
    
if __name__ == '__main__':

    res = json_request('getMe', {})
    print res
    pass
    
