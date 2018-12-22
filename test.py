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
    bot = sb.GoGBot()
    bot.getGames("onsale")
        
    

if __name__ == "__main__":
    main()