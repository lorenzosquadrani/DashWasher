import requests
import datetime
import sys
import time
import json
from tqdm import tqdm


def findFirstBlock(timeBound, index):
    step = 10000
    descending = True
    while step > 0 or time < timeBound:
        
        try:
            time = datetime.datetime.fromtimestamp(requests.get('https://sochain.com/api/v2/get_block/' + str(crypto) + '/' + str(index)).json()['data']['time']).strftime('%Y-%m-%d %H:%M:%S')
        except:
            index += 1
            continue
            
        if time < timeBound:
            index = index + step
            if descending is True:
                step = int(step / 2)
                descending = False
        else:
            index = index - step
            if descending is False:
                step = int(step / 2)
                descending = True

    return index + 1


def findLastBlock(timeBound, index):
    step = 10000
    time = ''
    
    while step > 0:
        exceed = False
        
        try: 
            response = requests.get('https://sochain.com/api/v2/get_block/' + str(crypto) + '/' + str(index + step))
            time = datetime.datetime.fromtimestamp(response.json()['data']['time']).strftime('%Y-%m-%d %H:%M:%S')
        except:
            if response == '<Response [404]>' or time>timeBound:
                exceed = True
            else:
                step+=1

        if exceed:
            step = int(step / 2)
        else:
            index = index + step
            
    return index


class Transaction:
    def __init__(self, sender, receiver):
        self.sender = sender
        self.receiver = receiver


def download(lowerB, upperB):

    transList = []
    nodeSet = set()

    blockIterator = lowerB

    while blockIterator <= upperB:

        r = requests.get('https://sochain.com/api/v2/get_block/' + str(crypto) + '/' + str(blockIterator))

        if r.status_code == 200:
            r = r.json()
        else:
            print("Unknown Error ({}), interrupting.".format(r.status_code))
            return 0

        print(datetime.datetime.fromtimestamp(r['data']['time']).strftime('%Y-%m-%d %H:%M:%S'), flush=True)

        for t in tqdm(r['data']['txs']):

            tx = requests.get('https://sochain.com/api/v2/get_tx/' + str(crypto) + '/' + t)
            if tx.status_code == 200:

                tx = tx.json()
                for i in tx['data']['inputs']:
                    nodeSet.add(i['address'])
                    for o in tx['data']['outputs']:
                        nodeSet.add(o['address'])
                        transList.append(Transaction(i['address'], o['address']))

            elif tx.status_code == 404:

                print('Error 404: invalid transaction id. Skipping it.')

                continue

            else:

                print("Unknown Error ({}), interrupting.".format(tx.status_code))
                break

        blockIterator += 1

    return nodeSet, transList


if __name__ == '__main__':

    crypto = sys.argv[1].upper()
    start = list(sys.argv[2])
    start[10] = ' '
    start = ''.join(start)
    end = list(sys.argv[3])
    end[10] = ' '
    end = ''.join(end)

    if len(sys.argv) > 4:
        fileRes = sys.argv[4]
    if len(sys.argv) == 6:
        cores = int(sys.argv[5])

        if crypto not in ['BTC', 'LTC', 'ZEC', 'DASH', 'DOGE']:

            sys.exit('CryptoCurrency must be one of the following:\n\
                  - Bitcon: BTC - Dash: DASH - Litecoin: LTC - Zetacoin: ZEC - Dogecoin: DOGE')

    print('Finding the index of the first block')
    lowerB = findFirstBlock(start, 1000000)
    print('Finding the index of the last block')
    upperB = findLastBlock(end, lowerB)
    print('Start reading the blocks')
    nodeSet, transList = download(lowerB, upperB)

    with open(fileRes, 'w') as f:
        print('Saving the graph in ' + fileRes)

        print('Key-sender Key-receiver', file=f)
        for t in transList:
            print(str(t.sender) + ' ' + str(t.receiver), file=f)
