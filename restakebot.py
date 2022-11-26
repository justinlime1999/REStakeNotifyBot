import requests
from telegram.ext import *
from telegram import ParseMode
import os
import json
import time

class RestakeBot:
    def __init__(self):
        self.starttime = time.time()
        self.load()
        self.updater = Updater(self.tapi)

    def load(self):
        if os.path.exists('info.json'):
            with open('info.json', 'r') as u:
                self.info = json.load(u)
                self.startheight = self.info['startheight']
                self.tapi = self.info['tapi']
                self.chatid = self.info['chatid']
                print('info loaded')
                
    def save(self):
        with open('info.json', 'w') as u:
            print('info saved')
            self.info['startheight'] = self.startheight
            json.dump(self.info, u)
    
    def refresh(self,height,bot):
        message = ''
        url = f'https://rest.unification.io/cosmos/tx/v1beta1/txs/block/{height}'
        refund_link = f"<a href='https://restake.app/unification/undvaloper1k03uvkkzmtkvfedufaxft75yqdfkfgvgsgjfwa'>reFUND</a>"
        height_link = f"<a href='https://explorer.unification.io/blocks/{height}'>{height}</a>"
        hot_wallet = 'und15eja9gte9e35gtnl70322kqjcdtscdu3tmrrv0'
        print(height)
        req = requests.get(url)

        if req.status_code == 200:
            txs = req.json()
            for t in txs['txs']:
                tx_type = t['body']['messages'][0]
                if t['body']['memo'] == 'REStaked by reFUND':
                    message += f'<b>[{refund_link}]</b>\n\n'
                    message += '<i>Auto-Compound Complete</i>\n\n'
                    for m in t['body']['messages']:
                        for ms in m['msgs']:
                            address = ms['delegator_address']
                            short_address = f'{address[0:3]}...{address[37:]}'
                            temp = f"<a href='https://explorer.unification.io/accounts/{address}'>{short_address}</a>"

                            message += f'<b>Delegator: </b>{temp}\n'
                            message += '<b>Compounded</b>: <i>' + str('{0:.2f}'.format(int(ms['amount']['amount'])/1000000000)) + ' FUND</i>\n\n'
                    message += '-----------------------------------------\n\n'
                    message += '<b>Fee paid by reFUND:</b> <i>' + str('{0:.4f}'.format(int(t['auth_info']['fee']['amount'][0]['amount'])/1000000000)) +' FUND</i>\n\n'
                    message += f'<b>Height:</b> <i>{height_link}</i>\n\n'
                    message += '<b>Compounding every:</b> <i>12 Hours</i>\n\n'
                    message += '<b>Minimum rewards needed to compound:</b> <i>0.01 FUND</i>\n\n'

                    print(message)
                    bot.send_message(parse_mode=ParseMode.HTML, chat_id=self.chatid, text=message, disable_web_page_preview=True)

                
                elif tx_type['@type'] == '/cosmos.authz.v1beta1.MsgGrant':
                    if tx_type['grantee'] == hot_wallet:
                        address = tx_type['granter']
                        short_address = f'{address[0:3]}...{address[37:]}'
                        temp = f"<a href='https://explorer.unification.io/accounts/{address}'>{short_address}</a>"

                        message += f'<b>[{refund_link}]</b>\n\n'
                        message += f'<i>Enabled Auto-Compounding</i>\n\n'
                        message += f'<b>Delegator:</b> {temp}'

                        print(message)
                        bot.send_message(parse_mode=ParseMode.HTML, chat_id=self.chatid, text=message, disable_web_page_preview=True)

                elif tx_type['@type'] == '/cosmos.authz.v1beta1.MsgRevoke':
                    if tx_type['grantee'] == hot_wallet:
                        address = tx_type['granter']
                        short_address = f'{address[0:3]}...{address[37:]}'
                        temp = f"<a href='https://explorer.unification.io/accounts/{address}'>{short_address}</a>"

                        message += f'<b>[{refund_link}]</b>\n\n'
                        message += f'<i>Disabled Auto-Compounding</i>\n\n'
                        message += f'<b>Delegator:</b> {temp}'

                        print(message)
                        bot.send_message(parse_mode=ParseMode.HTML, chat_id=self.chatid, text=message, disable_web_page_preview=True)             
                        
    def main(self):
        url = 'https://rest.unification.io/blocks/latest'
        height = int(requests.get(url).json()['block']['header']['height'])
        print('New height= ' + str(height))
        while(self.startheight < height):
            self.refresh(self.startheight,self.updater.bot)
            self.startheight += 1
        print('Caught up, waiting then recursing')
        time.sleep(60.0 - ((time.time() - self.starttime) % 60.0))
        print('Recursing')
        self.save()
        self.main()

new = RestakeBot()
new.main()


