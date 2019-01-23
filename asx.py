import requests
import datetime
from lxml import html
import pytz

Code=["xjo"]
Exdate = [""]
Option = ["B"]


def getascii(text):

    return ''.join([i if ord(i) < 128 else ' ' for i in text])

def getdata(c,d,o):
    retrievaldate = datetime.datetime.now(pytz.timezone('Australia/NSW')).strftime("%Y-%m-%d %H:%M:%S %Z%z")
    Datar=[]
    header = '{},{},{},{},{},{},{},{},{},{},{}\n'.format("Date Retrieved", "Code", "Expiry Date", "P/C", "Exercise","Bid", "Offer", "Last", "Volume", "Open interest",
                                                         "Margin Price")
    with open("%s.csv" % c, 'a+') as file:
        file.write(header)
    url = 'https://www.asx.com.au/asx/markets/optionPrices.do?by=underlyingCode&underlyingCode=' + '{}'.format(c) + '&expiryDate=' + '{}'.format(d) + '&optionType='+'{}'.format(o)
    print(url)
    data = requests.get(url)
    string_content = data.content
    tree = html.fromstring(string_content)




    # data
    Code = tree.xpath('//th[@class="row"]/a/text()')
    EDate = tree.xpath('//table[@class="datatable options"]/tbody/tr/td[1]/text()')
    PC = tree.xpath('//table[@class="datatable options"]/tbody/tr/td[2]/text()')
    Exercise = tree.xpath('//table[@class="datatable options"]/tbody/tr/td[3]/text()')
    Bid = tree.xpath('//table[@class="datatable options"]/tbody/tr/td[4]/text()')
    Offer = tree.xpath('//table[@class="datatable options"]/tbody/tr/td[5]/text()')
    Last = tree.xpath('//table[@class="datatable options"]/tbody/tr/td[6]/text()')
    Volume = tree.xpath('//table[@class="datatable options"]/tbody/tr/td[7]/text()')
    Openinterest = tree.xpath('//table[@class="datatable options"]/tbody/tr/td[8]/text()')
    MarginPrice = tree.xpath('//table[@class="datatable options"]/tbody/tr/td[9]/text()')



    Volume = [getascii(x) for x in Volume]
    Openinterest = [getascii(x) for x in Openinterest]
    MarginPrice = [getascii(x) for x in MarginPrice]

    # print(Volume)
   # writing data in csv

    with open("%s.csv" % c, 'a+') as file:
        for items in zip(Code, EDate, PC, Exercise, Bid, Offer, Last, Volume, Openinterest, MarginPrice):
            datawrites = '{},{},{},{},{},{},{},{},{},{},{}\n'.format(retrievaldate,
                items[0].replace(',', ''), items[1].replace(',', ' '), items[2].replace(',', ''),items[3].replace(',', ''), items[4].replace(',', ''),
                items[5].replace(',', ''), items[6].replace(',', ''), items[7].replace(',', ''), items[8].replace(',', ''), items[9].replace(',', ''))
            file.write(datawrites)
            Datar.append(datawrites)
            result= ''.join(Datar)
    return result

# print(getascii('\xa0'))

#
# for c,d,o in zip(Code, Exdate, Option):
#     result = getdata(c,d,o)
#     print(result)

