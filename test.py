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
    bot = sb.Bot()
    bot.queryDatabase(uri, username, password, (4.99, 29.99), -1, 1, 1)
    bot.printData()
    
        
    

if __name__ == "__main__":
    main()