#!/usr/bin/python

import logging
from json import loads


from reportlab.lib import utils
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Image, TableStyle
from reportlab.platypus import ListFlowable, ListItem
from reportlab.platypus import PageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle as PS

from libCommon import INI, CSV

styles = getSampleStyleSheet()
style_caption = PS(name='center', parent=styles['Normal'], fontSize=7, alignment=TA_CENTER)
h1 = PS(name = 'Heading1', fontSize = 12, leading = 16, leftIndent = 5 , fontName='Helvetica-Bold')
h2 = PS(name = 'Heading2', fontSize = 10, leading = 14, leftIndent = 10, fontName='Helvetica-Bold')
h3 = PS(name = 'Heading3', fontSize = 10, leading = 12, leftIndent = 15, fondName='Helvetica-Bold')
ticker = PS(name = 'Bullet1', fontSize = 8, leading = 8, alignment=TA_LEFT)
bullet = PS(name = 'Bullet2', fontSize = 8, leading = 8, alignment=TA_RIGHT)

def prep(*ini_list) :
    ret = {}
    for path, section, key, value_list in INI.loadList(*ini_list) :
        if section not in ret :
           ret[section] = {}
        ret[section][key] = value_list
    return ret

def main(report_ini, ini_list, csv_list) :
    doc = SimpleDocTemplate("image.pdf", pagesize=letter)
    try :
        return _main(doc, report_ini, ini_list, csv_list)
    except Exception as e :
        logging.error(e, exc_info=True)
        print e

def _main(doc,report_ini, ini_list, csv_list) :
    nasdaq_enrichment = filter(lambda x : 'nasdaq.csv', csv_list)
    if len(nasdaq_enrichment) > 0 :
       nasdaq_enrichment = nasdaq_enrichment[0]
    report_ini = prep(*report_ini)
    logging.debug(report_ini)

    toc = TableOfContents()
    toc.levelStyles = [h1, h2]

    ret = [ toc, PageBreak(), Paragraph('Portfolio Summary', h1) ]
    target = 'summary'
    summary = report_ini.get(target,{})
    target = 'images'
    image_list = summary.get(target,[])
    image_list = map(lambda path : alter_aspect(path, 3.5 * inch), image_list)
    target = 'captions'
    captions_list = summary.get(target,[])
    tbl = addTable(captions_list,image_list)
    ret.append(tbl)
    ret.append(PageBreak())
 
    key_list = report_ini.keys()
    portfolio_list = filter(lambda x : 'portfolio' in x, key_list)
    portfolio_list = sorted(portfolio_list)
    for target in portfolio_list :
        summary = report_ini.get(target,{})
        local_target = 'name'
        name = summary.get(local_target,target)
        if isinstance(name,list) :
           name = name[0]
        name = name.replace('_',' ')
        ret.append(Paragraph(name, h1))
        local_target = 'images'
        image_list = summary.get(local_target,[])
        image_list[0] = alter_aspect(image_list[0], 4 * inch)
        image_list[1] = alter_aspect(image_list[1], 3.5 * inch)
        local_target = 'captions'
        captions_list = summary.get(local_target,[])
        local_target = 'description'
        target_list = filter(lambda key : 'description' in key, summary)
        target_list = sorted(target_list)
        description_list = map(lambda key : summary.get(key,None), target_list)
        description_list = _modifyDescription(description_list)
        desc = []
        for description in addDescription(description_list,nasdaq_enrichment) :
            desc.append(description)
        tbl = addTable(captions_list,image_list, desc)
        logging.debug(tbl)
        ret.append(tbl)
        ret.append(PageBreak())
    logging.debug(ret)
    #doc.build(ret)
    doc.multiBuild(ret)

def alter_aspect(path, width) :
    im = utils.ImageReader(path)
    w, h = im.getSize()
    logging.debug((w, h))
    aspect = float(width / w)
    logging.info(aspect)
    return Image(path,width, h*aspect)

def addTable(name_list, image_list,description_list = []) :
    caption_list = map(lambda caption : Paragraph(caption, style_caption), name_list)
    logging.debug( description_list )
    if len(description_list) :
       description_list = [description_list]
    logging.debug( description_list )
    ret = [ image_list , caption_list, description_list]
    # here you add your rows and columns, these can be platypus objects
    return Table(data=ret)

def _modifyDescription(arg_list) :
    if len(arg_list) == 0 :
       return arg_list
    for i, value in enumerate(arg_list) : 
        if '{' != value[0] : continue
        value = value.replace("'",'"')
        value = loads(value)
        arg_list[i] = value
    return arg_list

def addDescription(arg_list, nasdaq_enrichment) :
    if not isinstance(arg_list,list) :
       return
    for i, value in enumerate(arg_list) :
        if isinstance(value,str) :
           value = Paragraph(value, styles["Normal"])
           yield value
        elif isinstance(value,dict) :
           for header in sorted(value.keys()) :
               content_list = value[header]
               logging.info(header)
               header = header.replace('_', ' ')
               header = Paragraph(header, h2)
               yield header
               for content in addDescriptionContent(content_list, nasdaq_enrichment) :
                   yield content

def addDescriptionContent(arg_list, nasdaq_enrichment) :
    if not isinstance(arg_list,list) :
       return
    arg_list = sorted(arg_list, key = lambda i: i['weight']) 
    logging.debug(arg_list)
    column_A, column_B = [], []
    for i, content in enumerate(arg_list) :
        target = 'weight'
        content[target] = "{}%".format(content[target]).rjust(8,' ')
        column_A.append(content['weight'])
        column_B.append(content['ticker'])
    column_C = CSV.grep(nasdaq_enrichment, *column_B)
    for key in column_C :
        description = '({0}) {2}'.format(*column_C[key])[:85]
        description = description.split(' - ')
        description = '<br/>'.join(description)
        column_C[key] = description
    missing_detail = "({0}) No info available for {0}"
    column_B = map(lambda key : column_C.get(key,missing_detail.format(key)),column_B)  
    for column in column_B :
        if 'No info' not in column : 
            logging.info(column)
            continue
        logging.warn(column)
    column_B = map(lambda x : Paragraph(x,ticker), column_B)
    column_A = map(lambda x : Paragraph(x,bullet), column_A)

    row_list = []
    for i, dummy in enumerate(column_A) :
        row = [column_A[i], column_B[i]]
        row_list.append(row)
    widths = [2.9*inch] * 2
    widths[0] = 0.7*inch
    logging.info(widths)
    ret = Table(data=row_list,colWidths=widths)
    #debugging tables
    ts = [('GRID', (0,0), (-1,-1), 0.25, colors.blue),
          ('TOPPADDING', (0,0), (-1,-1), 1),
          ('BOTTOMPADDING', (0,0), (-1,-1), 1),
          ]
    ts = [('TOPPADDING', (0,0), (-1,-1), 0),
          ('BOTTOMPADDING', (0,0), (-1,-1), 0),
          ('VALIGN',(0,0), (-1,-1), 'TOP'),]
    ts = TableStyle(ts)
    ret.setStyle(ts)
    logging.debug(ret)
    yield ret

if __name__ == '__main__' :

   from glob import glob
   import os,sys
   from libCommon import TIMER

   pwd = os.getcwd()

   dir = pwd.replace('bin','log')
   name = sys.argv[0].split('.')[0]
   log_filename = '{}/{}.log'.format(dir,name)
   log_msg = '%(module)s.%(funcName)s(%(lineno)s) %(levelname)s - %(message)s'
   logging.basicConfig(filename=log_filename, filemode='w', format=log_msg, level=logging.INFO)

   local = pwd.replace('bin','local')
   ini_list = glob('{}/*.ini'.format(local))
   report_ini = glob('{}/report_generator.ini'.format(local))
   #report_ini = sorted(report_ini)

   csv_list = glob('{}/*.csv'.format(local))
   logging.info("started {}".format(name))
   elapsed = TIMER.init()
   main(report_ini,ini_list, csv_list)
   logging.info("finished {} elapsed time : {}".format(name,elapsed()))
