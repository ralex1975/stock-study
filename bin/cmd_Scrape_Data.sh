#!/bin/bash
python=python3
function scrape_prices {
   $python cmd_Scrape_Benchmarks.py
   #Execution speed for main : , seconds : 58.5
   $python cmd_Scrape_Tickers.py
   #Execution speed for main : hours : 9.0, minutes : 8.0, seconds : 5.71
}
function scrape_background {
   $python cmd_Scrape_Fund.py
   #Execution speed for main : minutes : 11.0, seconds : 24.71
   $python cmd_Scrape_Stock.py
   #Execution speed for main : minutes : 4.0, seconds : 49.73
   $python cmd_Scrape_Stock_Sector.py
   #Execution speed for main : minutes : 23.0, seconds : 56.14
}

set -eux
scrape_prices
scrape_background
