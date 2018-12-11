# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 11:22:14 2018

@author: afrom
"""

import SteamBot as sb

def main():
    bot = sb.SteamBot()
    bot.getGames("sales")
    bot.printDataInfo()

if __name__ == "__main__":
    main()