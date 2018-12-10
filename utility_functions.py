# -*- coding: utf-8 -*-
"""
Created on Sun Dec  9 10:21:08 2018

@author: afrom
"""

def getFrontPageInfo(item):
        #Inputs a tab_item html class from steam store page
        #Outputs a tuple of information that has been collected
        #Collects only from the front page of steam
        #So just a summary of any given tab
        
        info_tup = ()
        game_price = item.find(class_ = "discount_final_price")
        if game_price is None:
            game_price = "Not yet announced"
        else:
            game_price = game_price.get_text()
        #Maybe game tags should be processed a bit more
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
            
        #game_info_add = getGamePageInfo(URL)
                
        info_tup = (bundle_status, game_price, game_discount, game_tags_proc, URL)
        return info_tup
def fixGameReviews(game_review_string):
    for (i, ch) in enumerate(game_review_string):
        if(ch == "<"):
            return game_review_string[:i]
    
def getGamesInfo(game_container):
    #Returns tuple of information 
    #(Bundle status, price, discount percent, tags, URL)
    #Game reviews currently broken
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

    #Checks to see if game is discounted or not
    #If the game is not discounted...
    if game_discount is None or len(game_discount.get_text()) < 2:
        game_discount = "-0%"
        game_price = game_container.find(class_ = "search_price")
        if game_price is None:
            game_price = "Not yet announced"
        else:
            game_price = game_price.get_text().strip()
    else:
        #If the game is discounted...
        game_discount = game_discount.get_text().strip()
        game_price_lst = game_container.find(class_ = "search_price").get_text().split("$")
        if "Free" in game_price_lst[1]:
            game_price = "$0.00"
        else:
            game_price = "$" + game_price_lst[2].strip()
            
    URL = game_container.get("href")
    if "bundle" in URL:
        game_bundle = "Item is a bundle"
    else:
        game_bundle = "Item is not a bundle"
        
    
    
    return (game_bundle, game_price, game_discount, game_reviews, game_date, URL)

def getValidName(string):
    string = string.lower()
    if "top" in string:
        return "topselling"
    elif "new" in string or "trending" in string:
        return "newandtrending"
    elif "unreleased" in string or "upcoming" in string:
        return "popularupcoming"
    elif "sale" in string or "deal" in string:
        return "specials"
    
    return "error"
    