import logging
import csv as _csv
from libCommon import FTP

'''

Web Scraping Utils

'''
class TRANSFORM_PARTICIPANT() :
      _type = {
              'A' : 'Agency Quote'
              , 'C' : 'Electronic Communications Network (ECN)'
              , 'E' : 'Exchange'
              , 'M' : 'Market Maker'
              , 'N' : 'Miscellaneous'
              , 'O' : 'Order Entry Firm'
              , 'P' : 'NASDAQ Participant'
              , 'Q' : 'Query Only Firm'
              , 'S' : 'Specialist'
              }
      @classmethod
      def Type(cls,row) :
          target = 'MP Type'
          value = row.get(target,'') 
          replace = cls._type.get(value,value)
          row[target] = replace
          return row
class TRANSFORM_STOCK() :
      market = { 'Q' : 'NASDAQ Global Select MarketSM'
                   , 'G' : 'NASDAQ Global MarketSM'
                   , 'S' : 'NASDAQ Capital Market'
                   }
      finance = { 'D' : 'Deficient: Issuer Failed to Meet NASDAQ Continued Listing Requirements'
                 , 'E' : 'Delinquent: Issuer Missed Regulatory Filing Deadline'
                 , 'Q' : 'Bankrupt: Issuer Has Filed for Bankruptcy'
                 , 'N' : 'Normal (Default): Issuer Is NOT Deficient, Delinquent, or Bankrupt.'
                 , 'G' : 'Deficient and Bankrupt'
                 , 'H' : 'Deficient and Delinquent'
                 , 'J' : 'Delinquent and Bankrupt'
                 , 'K' : 'Deficient, Delinquent, and Bankrupt'
                 }
      exchange = {
              'A' : 'NYSE MKT'
              , 'N' : 'New York Stock Exchange (NYSE)'
              , 'P' : 'NYSE ARCA'
              , 'Z' : 'BATS Global Markets (BATS)'
              , 'V' : "Investors' Exchange, LLC (IEXG)"
              }
      @classmethod
      def Market(cls,row) :
          target = 'Market Category'
          value = row.get(target,'') 
          replace = cls.market.get(value,value)
          row[target] = replace
          return row
      @classmethod
      def Finance(cls,row) :
          target = 'Financial Status'
          value = row.get(target,'') 
          replace = cls.finance.get(value,value)
          row[target] = replace
          return row
      @classmethod
      def Exchange(cls,row) :
          target = 'Listing Exchange'
          value = row.get(target,'') 
          replace = cls.exchange.get(value,value)
          row[target] = replace
          return row
      @classmethod
      def Exchange2(cls,row) :
          target = 'Exchange'
          value = row.get(target,'') 
          replace = cls.exchange.get(value,value)
          row[target] = replace
          return row
class TRANSFORM_FUND() :
      _Type = { 'AN' : 'Annuities'
              , 'MF' : 'Mutual Fund'
              , 'MS' : 'Supplemental Mutual Fund'
              , '$$' : 'Money Market Fund'
              , '$S' : 'Supplemental Money Market Fund'
              , 'SP' : 'Structured Products'
              , 'US' : 'UIT Supplemental List'
              , 'UT' : 'UIT News Media List'
              }
      _Category = {
              'M' : 'Variable'
              , 'N' : 'Equity Indexed'
              , 'O' : 'Open-end'
              , 'C' : 'Closed-end'
              , 'A' : 'General Purpose'
              , 'G' : 'Govt. Securities'
              , 'X' : 'Tax-Exempt'
              , 'R' : 'Access Transaction'
              , 'S' : 'Tax Driven Structure'
              , 'T' : 'Buffered Note'
              , 'U' : 'Principal Protected Note'
              , 'V' : 'Levered Note'
              , 'W' : 'Enhanced Income Note'
              , 'E' : 'Equity'
              , 'F' : 'Not Used/Reserved'
              , 'D' : 'Fixed Income'
              }
      @classmethod
      def Type(cls,row) : 
          target = 'Type'
          value = row.get(target,'') 
          replace = cls._Type.get(value,value)
          row[target] = replace
          return row
      @classmethod
      def Category(cls,row) : 
          target = 'Category' 
          value = row.get(target,'') 
          replace = cls._Category.get(value,value)
          row[target] = replace
          return row
class NASDAQ_FILTER() :
      @classmethod
      def test(cls,data) :
          test = []
          ret = []
          for row in data:
              curr, row = cls._test(row,ret,test)
              curr.append(row)
          return ret, test
      @classmethod
      def _test(cls,row,live,test) :
          ret = live
          flag = filter(lambda x : 'Test' in x , row.keys())
          flag = list(flag)
          flag = map(lambda x : row.pop(x,x) , flag)
          flag = list(flag)
          flag = filter(lambda x : x is not None, flag)
          flag = list(flag)
          flag = filter(lambda x : 'Y' in x, flag)
          flag = list(flag)
          flag = len(flag) > 0
          if flag :
             ret = test
          return ret, row
      @classmethod
      def ETF(cls,row,stock,etf) :
          ret = stock
          flag = filter(lambda x : 'ETF' in x , row.keys())
          flag = map(lambda x : row.get(x,x) , flag)
          flag = filter(lambda x : 'Y' in x , flag)
          flag = list(flag)
          flag = len(flag) > 0
          if flag :
             ret = etf
          return ret
      @classmethod
      def alias(cls,row) :
          stock_list = filter(lambda x : 'Symbol' in x , row.keys())
          stock_list = list(stock_list)
          stock_name = map(lambda x : row.get(x,x), stock_list)
          stock_name = list(set(stock_name))
          if len(stock_name) == 1 :
             return stock_name[0], {}
          stock_name = sorted(stock_name)
          nasdaq = filter(lambda x : 'NASDAQ' in x , stock_list)
          nasdaq = list(nasdaq)
          stock_list = list(set(stock_list) - set(nasdaq))
          stock_value = map(lambda x : row.get(x,x), stock_list)
          stock_alt = dict(zip(stock_list,stock_value))
          logging.info(nasdaq)
          logging.debug(stock_alt)
          nasdaq = map(lambda x : row.get(x,x), nasdaq)
          nasdaq = list(nasdaq)
          return nasdaq[0], stock_alt

class NASDAQ_TRANSFORM() :
      @classmethod
      def fund_ticker(cls,fund) :
          target = 'Fund Symbol'
          ret = fund.get(target,None)
          return ret

      @classmethod
      def stock_list(cls,row_list) :
          stock = set([])
          etf = set([])
          alias = {}
          for row in row_list :
              curr = NASDAQ_FILTER.ETF(row,stock,etf)
              exchange = filter(lambda x : 'Exchange' in x , row.keys())
              exchange = map(lambda x : row.get(x,x) , exchange)
              exchange = list(exchange)
              if len(exchange) > 0 :
                 exchange = exchange[0]
              if isinstance(exchange,str) :
                 if 'NYSE' not in exchange :
                    logging.warn(exchange)
                    continue
              name, alt_name = NASDAQ_FILTER.alias(row)
              curr.add(name)
              if len(alt_name) > 0 :
                 alias[name] = alt_name
          return stock, etf, alias
class NASDAQ() :
      url = 'ftp.nasdaqtrader.com'
      file_list = ['bondslist.txt', 'bxoptions.txt', 'bxo_lmm.csv', 'bxtraded.txt'
              , 'gmniListedStrikesWithOptionIds.zip', 'iseListedStrikesWithOptionIds.zip', 'mcryListedStrikesWithOptionIds.zip', 'mfundslist.txt', 'mpidlist.txt'
              , 'nasdaqlisted.txt', 'nasdaqtraded.txt', 'options.txt', 'otclist.txt', 'otherlisted.txt'
              , 'pbot.csv', 'phlxListedStrikesWithOptionIds.zip', 'phlxoptions.csv', 'phlxStrikesOld.zip', 'psxtraded.txt'
              , 'regnms', 'regsho', 'regshopilot', 'regshopilotlist', 'shorthalts'
              , 'TradingSystemAddsDeletes.txt']

      def __init__(self,ftp,*file_list) :
          self.ftp = ftp
          self.file_list = file_list
      def __call__(self):
          logging.info(dir(self))
          ret = FTP.LIST(self.ftp, pwd = 'symboldirectory')
          ret = set(ret)
          file_list = set(NASDAQ.file_list)
          lhs = ret - file_list
          rhs = file_list - ret
          if len(lhs) > 0 :
              logging.warn(lhs)
          if len(rhs) > 0 :
              logging.warn(rhs)
          for i, name in enumerate(self.file_list) :
              logging.info((i, name))
          return ret

      def listed(self) :
          raw = FTP.GET(self.ftp, pwd = self.file_list[9])
          temp = NASDAQ.to_dict(raw)
          ret, test_list = NASDAQ_FILTER.test(temp)
          ret = map(lambda row : TRANSFORM_STOCK.Market(row), ret)
          ret = map(lambda row : TRANSFORM_STOCK.Finance(row), ret)
          return ret, raw 
      def traded(self) :
          raw = FTP.GET(self.ftp, pwd = self.file_list[10])
          temp = NASDAQ.to_dict(raw)
          ret, test_list = NASDAQ_FILTER.test(temp)
          ret = map(lambda row : TRANSFORM_STOCK.Market(row), ret)
          ret = map(lambda row : TRANSFORM_STOCK.Finance(row), ret)
          ret = map(lambda row : TRANSFORM_STOCK.Exchange(row), ret)
          return ret, raw 
      def other(self) :
          raw = FTP.GET(self.ftp, pwd = self.file_list[13])
          temp = NASDAQ.to_dict(raw)
          ret, test_list = NASDAQ_FILTER.test(temp)
          ret = map(lambda row : TRANSFORM_STOCK.Exchange2(row), ret)
          return ret, raw
      def funds(self) :
          raw = FTP.GET(self.ftp, pwd = self.file_list[7])
          ret = NASDAQ.to_dict(raw)
          ret = map(lambda row : TRANSFORM_FUND.Type(row), ret)
          ret = map(lambda row : TRANSFORM_FUND.Category(row), ret)
          ret = list(ret)
          return ret, raw
      def bonds(self) :
          raw = FTP.GET(self.ftp, pwd = self.file_list[0])
          ret = NASDAQ.to_dict(raw)
          return ret, raw
      def participants(self) :
          raw = FTP.GET(self.ftp, pwd = self.file_list[8])
          ret = NASDAQ.to_dict(raw)
          ret = map(lambda row : TRANSFORM_PARTICIPANT.Type(row), ret)
          return ret, raw
      def stock_list(self) :
          listed, csv = self.listed()
          #traded, csv = self.traded()
          other, csv = self.other()
          _list = []
          #_list += listed + traded + other
          _list += list(listed) + list(other)
          stock, etf, alias = NASDAQ_TRANSFORM.stock_list(_list)
          stock = sorted(list(stock))
          etf = sorted(list(etf))
          logging.info(('Stocks',len(stock)))
          logging.info(('ETF',len(etf)))
          return stock, etf, alias 
      def fund_list(self) :
          ret = {}
          fund_list, csv = self.funds()
          for fund in fund_list :
              target = 'Fund Family Name' 
              name = fund.pop(target,target)
              if name not in ret :
                 ret[name] = []
              ret[name].append(fund)
          for family in ret :
              logging.debug((family,ret[family]))
          logging.info(('Funds',len(fund_list)))
          return fund_list

      @classmethod
      def init(cls) :
          ftp = FTP.init(server=cls.url)
          file_list = map(lambda x : '/symboldirectory/{}'.format(x), cls.file_list)
          ret = cls(ftp,*file_list)
          return ret
      @classmethod
      def to_dict(cls,ret) :
          data = str(ret)
          reader = _csv.DictReader(data.split('\n'), delimiter='|')
          ret = []
          for row in reader:
              ret.append(row)
          return ret

if __name__ == '__main__' :
   import logging
   import sys
   from libCommon import ENVIRONMENT

   env = ENVIRONMENT()
   log_msg = '%(module)s.%(funcName)s(%(lineno)s) %(levelname)s - %(message)s'
   logging.basicConfig(stream=sys.stdout, format=log_msg, level=logging.INFO)

   obj = NASDAQ.init()
   #listed, csv = obj.listed()
   #funds, csv = obj.funds()
   #bonds, csv = obj.bonds()
   #traded, csv = obj.traded()
   #other, csv = obj.other()
   #participants, csv = obj.participants()
   #print obj()

   stock, etf, alias = obj.stock_list()
   print (stock[:10])
   #obj.fund_list()
