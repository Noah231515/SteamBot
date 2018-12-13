# -*- coding: utf-8 -*-
"""
Created on Sun Dec  9 10:21:08 2018

@author: afrom
"""
from neo4j import GraphDatabase

def getFrontPageInfo(item):
        #Inputs a tab_item html class from steam store page
        
        info_tup = ()
        game_price = item.find(class_ = "discount_final_price")
        
        if game_price is None:
            game_price = "Not yet announced"
        else:
            game_price = game_price.get_text()

        game_tags = item.find_all(class_ = "top_tag")
        game_tags_proc = [t.get_text().strip().strip(',') for t in game_tags]
        game_discount = item.find(class_ = "discount_pct")
        
        if game_discount is None:
            game_discount = "-0%"
        else:
            game_discount = game_discount.get_text()
        URL = item.get('href')
        
        if "bundle" in URL:
            bundle_status = "Item is a bundle"
        else:
            bundle_status = "Item is not a bundle"
            
        info_tup = (bundle_status, game_price, game_discount, game_tags_proc, URL)
        return info_tup
    
def fixGameReviews(game_review):
    for (i, ch) in enumerate(game_review):
        if(ch == "<"):
            return game_review[:i]
    
def getGameInfo(game_container):
    #Input is a tab_item html class from steam search pages

    game_date = game_container.find(class_ = "search_released")
    if game_date is None:
        game_date = "Not yet released"
    else:
        game_date = game_date.get_text()
        
    game_reviews = game_container.find(class_ = "search_review_summary")
    if game_reviews is None:
        game_reviews = "Currently No Reviews"
    else:
        game_reviews = fixGameReviews(game_reviews["data-tooltip-html"])

    game_discount = game_container.find(class_ = "search_discount")


    if game_discount is None or len(game_discount.get_text()) < 2:
        game_discount = "-0%"
        game_price = game_container.find(class_ = "search_price")
        if game_price is None:
            game_price = "Not yet announced"
        else:
            game_price = game_price.get_text().strip()
    else:

        game_discount = game_discount.get_text().strip()
        game_price_lst = game_container.find(class_ = "search_price").get_text().split("$")
        if "Free" in game_price_lst[1]:
            game_price = "$0.00"
        else:
            game_price = "$" + game_price_lst[2].strip()
            
    URL = game_container.get("href")
    if "bundle" in URL:
        game_bundle = "Item is a bundle"
        game_date = "No release date"
    else:
        game_bundle = "Item is not a bundle"
        
    
    
    return (game_bundle, game_price, game_discount, game_reviews, game_date, URL)

def getValidName(category_name):
    category_name = category_name.lower()
    if "top" in category_name:
        return "topselling"
    elif "new" in category_name or "trending" in category_name:
        return "newandtrending"
    elif "unreleased" in category_name or "upcoming" in category_name:
        return "popularupcoming"
    elif "sale" in category_name or "deal" in category_name:
        return "specials"
    
    return "error"


def createNodeInfo(tx, game_name, game_bundle_status, game_price, game_discount, game_reviews, game_date, URL):
    node = tx.run("create (g: Steam_Games {name: $game_name}) "
                  "set g.game_bundle_status = $game_bundle_status "
                  "set g.price = $game_price "
                  "set g.game_discount = $game_discount "
                  "set g.game_reviews = $game_reviews "
                  "set g.game_date = $game_date "
                  "set g.URL = $URL", game_name = game_name, game_bundle_status = game_bundle_status, game_price = game_price, game_discount = game_discount, game_reviews = game_reviews, game_date = game_date, URL = URL)
    return node

def addDatabaseInfo(uri, username, password, platform, game_dict):
    #Currently can input information into DB
    #Does not account for the error raised by constraint
    #Works
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    with driver.session() as session:
        for game, game_tuple in game_dict.items():
            game_name = game
            game_bundle = game_tuple[0]
            game_price = game_tuple[1]
            game_discount = game_tuple[2]
            game_reviews = game_tuple[3]
            game_date = game_tuple[4]
            URL = game_tuple[5]
            session.write_transaction(createNodeInfo, game_name, game_bundle, game_price, game_discount, game_reviews, game_date, URL)
            
    

def updateDatabaseInfo():
    pass