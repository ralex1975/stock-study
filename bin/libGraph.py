#!/usr/bin/python

import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class LINE :
      @staticmethod
      def plot(lines,**kwargs) :
          target = 'style'
          style = kwargs.get(target,'o')
          target = 'xlabel'
          xlabel = kwargs.get(target,None)
          target = 'ylabel'
          ylabel = kwargs.get(target,None)
          target = 'title'
          title = kwargs.get(target,None)
          LINE._plot(lines)
          if xlabel is not None : plt.xlabel(xlabel)
          if ylabel is not None : plt.ylabel(ylabel)
          if title is not None : plt.title(title)
      @staticmethod
      def _plot(lines) :
          for data, label in LINE._xy(lines) :
              logging.info(data)
              logging.info(label)
              data.plot(label=label)
      @staticmethod
      def _xy(data) :
          for key in sorted(data.keys()) :
              yield data[key], key
class BAR :
      @staticmethod
      def plot(bar, **kwargs) :
          target = 'style'
          style = kwargs.get(target,'o')
          target = 'xlabel'
          xlabel = kwargs.get(target,None)
          target = 'ylabel'
          ylabel = kwargs.get(target,None)
          target = 'title'
          title = kwargs.get(target,None)
          target = 'width'
          width = kwargs.get(target,11)
          target = 'height'
          height = kwargs.get(target,7)
          plt.figure(figsize=(width, height))
          BAR._plot(bar)
          if xlabel is not None : plt.xlabel(xlabel)
          if ylabel is not None : plt.ylabel(ylabel)
          if title is not None : plt.title(title)
      @staticmethod
      def _plot(bar) :
          label, data, pos = BAR._xy(bar)
          plt.barh(pos, data, align='center', alpha=0.5)
          plt.yticks(pos, label)
      @staticmethod
      def _xy(data) :
          label_list = []
          data_list = []
          if len(data) == 0 :
             y_pos = np.arange(len(label_list))
             return label_list, data_list, y_pos
          sorted_list = sorted((value, key) for (key,value) in data.items())
          if sorted_list is None :
             y_pos = np.arange(len(label_list))
             return label_list, data_list, y_pos
          sorted_list.reverse() 
          for key, value in sorted_list :
              label_list.append(value)
              data_list.append(key)
          y_pos = np.arange(len(label_list))
          label_list = map(lambda label : BAR._label(label), label_list)
          return label_list, data_list, y_pos
      @staticmethod
      def _label(ret) :
          from textwrap import wrap
          if '_' not in ret : return ret
          ret =  ret.replace('_',' ')
          ret = '\n'.join(wrap(ret, 15))
          return ret

class POINT :

      @staticmethod
      def plot(points, **kwargs) :
          target = 'x'
          x_column_name = kwargs.get(target,'returns')
          target = 'y'
          y_column_name = kwargs.get(target,'risk')
          target = 'style'
          style = kwargs.get(target,'o')
          target = 'xlabel'
          xlabel = kwargs.get(target,None)
          target = 'ylabel'
          ylabel = kwargs.get(target,None)
          target = 'title'
          title = kwargs.get(target,None)
          POINT._plot(points, x_column_name, y_column_name, style)
          if xlabel is not None : plt.xlabel(xlabel)
          if title is not None : plt.title(title)
          if ylabel is not None : plt.ylabel(ylabel)

      @staticmethod
      def _plot(points, column_x, column_y, style) :
          for x, y, label in POINT._xy(points,column_x,column_y) :
              #plt.scatter(x,y)
              #ax = point.plot(x='x', y='y', ax=ax, style='bx', label='point')
              plt.plot(x,y,style, label=label)
      @staticmethod
      def _xy(data,x,y) :
          for key in sorted(data.keys()) :
              pt = data[key]
              yield pt[x], pt[y], key

def save(path) :
    #from matplotlib.pyplot import figure
    plt.legend()
    #plt.autoscale()
    #plt.gcf().subplots_adjust(left=0.15)
    plt.savefig(path)
    plt.clf()
    plt.cla()
    plt.close()

if __name__ == '__main__' :

   from glob import glob
   import os,sys
   from libCommon import TIMER

   pwd = os.getcwd()
   local = pwd.replace('bin','local')
   portfolio_ini = glob('{}/yahoo_sharpe_method1*portfolios.ini'.format(local))
   ini_list = glob('{}/*.ini'.format(local))
   file_list = glob('{}/historical_prices/*pkl'.format(local))

   dir = pwd.replace('bin','log')
   name = sys.argv[0].split('.')[0]
   log_filename = '{}/{}.log'.format(dir,name)
   log_msg = '%(module)s.%(funcName)s(%(lineno)s) %(levelname)s - %(message)s'
   logging.basicConfig(filename=log_filename, filemode='w', format=log_msg, level=logging.INFO)

   logging.info("started {}".format(name))
   elapsed = TIMER.init()
   logging.info("finished {} elapsed time : {} ".format(name,elapsed()))
