#!/usr/bin/env python3

from datetime import datetime, timedelta
import json, requests


verify_ssl_cert=True
utc_offset=None

# https://www.easyenergy.com/nl/energietarieven
tax_stroom_ct = 1.962 + 4.010 + 3.325 + 0.104
tax_gas_ct = 9.81 + 1.714 + 39.591 + 9.429

def get_easy_data(url, ts1, ts2):
    global verify_ssl_cert

    ts_start = ts1.isoformat()+'Z'
    ts_end = ts2.isoformat()+'Z'

    html=requests.get(url, params={'startTimestamp': ts_start, 'endTimestamp': ts_end} , verify=verify_ssl_cert)
    try:
        data=json.loads(html.content)
    except Exception as e:
        from sys import stderr
        print(html.status_code, html.content, file=stderr)
        raise e

    for d in data:
        assert len(d.keys())==4
        assert all(x in d.keys() for x in ['Timestamp', 'SupplierId', 'TariffUsage', 'TariffReturn'])
        assert d['SupplierId']==0
        yield d


def gas_data(ts1, ts2):
    url='https://mijn.easyenergy.com/nl/api/tariff/getlebatariffs'
    last_tarrif = None

    for d in get_easy_data(url, ts1, ts2):
        ts, tarrif = d['Timestamp'], d['TariffUsage']
        if tarrif != last_tarrif:
            yield ts, tarrif
            last_tarrif = tarrif


def stroom_data(ts1, ts2):
    url='https://mijn.easyenergy.com/nl/api/tariff/getapxtariffs'

    for d in get_easy_data(url, ts1, ts2):
        ts, tarrif = d['Timestamp'], d['TariffUsage']
        yield ts, tarrif


def pretty_ts(ts):
    global utc_offset

    utc=datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S+00:00')
    local=utc+utc_offset
    return local.strftime('%d %b  %H:%M')


def main():
    global utc_offset

    now=datetime.now().replace(minute=0, second=0, microsecond=0)

    if utc_offset == None:
        utc_offset = now - datetime.utcfromtimestamp(now.timestamp())

    if now.hour < 6:
        utc_gas = now.replace(hour=0) - utc_offset
    else:
        utc_gas = now.replace(hour=6) - utc_offset

    utc_stroom  = now - utc_offset
    utc_end = now + timedelta(hours=48) - utc_offset

    print('Gas')
    print('===')
    print(f'incl. EUR {tax_gas_ct/100:.2f} belasting:\n')
    for ts, tarrif in gas_data(utc_gas, utc_end):
        tarrif+=tax_gas_ct/100
        print(f'{pretty_ts(ts)}: EUR {tarrif:4.2f}')

    print('')
    print('Stroom')
    print('======')
    print(f'incl. {tax_stroom_ct:.1f} ct belasting:\n')
    for ts, tarrif in stroom_data(utc_stroom, utc_end):
        tarrif *= 100
        tarrif+=tax_stroom_ct
        print(f'{pretty_ts(ts)}: {tarrif:5.1f} ct')


if __name__ == '__main__':
    main()
