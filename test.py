# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 11:22:14 2018

@author: afrom
"""

import SteamBot as sb
import utility_functions as uf

def main():
    uri = "bolt://localhost:7687"
    username = "Noah"
    password = "password" 
    bot = sb.SteamBot()
    bot.getGames("sales")
    games_dict = bot.getBotData()[0]
    #bot.getGames("sales")
    uf.addDatabaseInfo(uri, username, password, bot.platform, games_dict)

if __name__ == "__main__":
    main()