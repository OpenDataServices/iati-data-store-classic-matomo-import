
import argparse

import apachelogs
import requests



APACHE_LOG_FILE_FORMAT =  "%{REQUEST_SCHEME}x://%v %h %t \"%r\" %>s %O \"%{Referer}i\" \"%{User-Agent}i\""

# Should be lower case
EXCLUDED_USER_AGENTS = (
    'adsbot-google',
    'ask jeeves',
    'baidubot',
    'ccooter/',
    'crawl',
    'echoping',
    'exabot',
    'feed',
    'googlebot',
    'ia_archiver',
    'libwww',
    'mediapartners-google',
    'msnbot',
    'netcraftsurvey',
    'panopta',
    'pingdom.com_bot_',
    'robot',
    'spider',
    'surveybot',
    'twiceler',
    'voilabot',
    'yahoo',
    'yandex',
    'zabbix',
    'googlestackdrivermonitoring',
    'uptimerobot',
    'apachebench',
)

CUSTOM_DIMENSION_BACKEND = 10
CUSTOM_DIMENSION_FORMAT = 6
CUSTOM_DIMENSION_HTTP_STATUS = 7
CUSTOM_DIMENSION_METHOD = 8
CUSTOM_DIMENSION_SIZE = 9

def main():

    parser = argparse.ArgumentParser(
            description="Import HTTP access logs to Matomo. ",
            epilog="https://github.com/OpenDataServices/iati-data-store-classic-matomo-import"
        )

    parser.add_argument('file', type=str, nargs='?')
    parser.add_argument('host', type=str, nargs='?')
    parser.add_argument('token', type=str, nargs='?')
    parser.add_argument('siteid', type=int, nargs='?')

    args = parser.parse_args()

    config = Config(
        args.file,
        args.host,
        args.token,
        args.siteid
    )

    entries = parse_logs(config)

    for entry in entries:
        print(entry)
        send_to_matomo(config, entry)

def parse_logs(config):
    entries = []
    parser = apachelogs.LogParser(APACHE_LOG_FILE_FORMAT)
    with open(config.file) as fp:
        for entry in parser.parse_lines(fp):
            entries.extend(process_entry(config, entry))
    return entries


def process_entry(config, entry):

    method, path, httpversion = entry.request_line.split(" ")

    # We only want API accesses
    if not path.startswith("/api"):
        return []

    # Filter out known bots?
    user_agent = entry.headers_in["User-Agent"].lower()
    for s in EXCLUDED_USER_AGENTS:
        if s in user_agent:
            return []

    # We do want to include this line
    return [entry_to_matomo_format(config, entry)]


def entry_to_matomo_format(config, entry):

    #print(entry.__dict__)

    method, path, httpversion = entry.request_line.split(" ")

    path_params_bits = path.split('?',2)
    path_before_params = path_params_bits[0]

    url = entry.variables['REQUEST_SCHEME'] + '://' +  entry.virtual_host  + path

    date, time = entry.request_time.isoformat(sep=' ').split()

    out = {
        'rec': 1,
        'apiv': 1,
        'idsite': config.siteid,
        'token_auth': config.token,
        'url': url,
        'urlref': entry.headers_in["Referer"],
        'ua': entry.headers_in["User-Agent"],
        'cip': entry.remote_host,
        'cdt': '%s %s' % (date, time.replace('-', ':')),
        'queuedtracking': '0',
        'dimension'+str(CUSTOM_DIMENSION_BACKEND): 'backend',
        'dimension'+str(CUSTOM_DIMENSION_HTTP_STATUS): entry.final_status,
        'dimension'+str(CUSTOM_DIMENSION_METHOD): method,
        'dimension'+str(CUSTOM_DIMENSION_SIZE): entry.bytes_out,
    }

    if path.startswith("/api/1/access"):
        out['download'] = out['url']
        if path_before_params.endswith('.csv'):
            out['dimension'+str(CUSTOM_DIMENSION_FORMAT)] = 'csv'
        elif path_before_params.endswith('.xml'):
            out['dimension'+str(CUSTOM_DIMENSION_FORMAT)] = 'xml'
        elif path_before_params.endswith('.json'):
            out['dimension'+str(CUSTOM_DIMENSION_FORMAT)] = 'json'

    return out

def send_to_matomo(config, entry):
    r = requests.get(config.host+'/matomo.php', params=entry)
    if r.status_code == 200:
        print("SUCCESS")
    else:
        print("FAIL STATUS=" + str(r.status_code))

class Config:
    def __init__(self, file, host, token, siteid):
        self.file = file
        self.host = host
        self.token = token
        self.siteid = siteid


if __name__ == '__main__':
    main()