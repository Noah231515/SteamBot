# -*- coding: utf-8 -*-
"""
Created on Sun Dec  9 10:21:08 2018

@author: afrom
"""
from neo4j import GraphDatabase
from neo4j import exceptions as ex
import SteamBot as sb

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
    no_date = "Not Yet Released"
    no_reviews = "Currently No Reviews"
    no_price = "Not Yet Announced"
    no_bundle_date = "No Release Date for Bundles"

    game_date = game_container.find(class_ = "search_released")
    if game_date is None:
        game_date = no_date
    else:
        game_date = game_date.get_text()
        
    game_reviews = game_container.find(class_ = "search_review_summary")
    if game_reviews is None:
        game_reviews = no_reviews
    else:
        game_reviews = fixGameReviews(game_reviews["data-tooltip-html"])

    game_discount = game_container.find(class_ = "search_discount")


    if game_discount is None or len(game_discount.get_text()) < 2:
        game_discount = "-0%"
        game_price = game_container.find(class_ = "search_price")
        if game_price is None:
            game_price = no_price
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
    if "bundle" in URL or "pack" in URL:
        game_bundle = True
        game_date = no_bundle_date
    else:
        game_bundle = False
        
    
    
    return (game_bundle, game_price, game_discount, game_reviews, game_date, URL)

def getValidName(category_name):
    category_name = category_name.lower()
    if "top" in category_name:
        return "topselling"
    elif "new" in category_name or "trending" in category_name:
        return "newandtrending"
    elif "unreleased" in category_name or "upcoming" in category_name:
        return "popularupcoming"
    elif "sale" in category_name or "deal" or "special" in category_name:
        return "specials"
    
    return "error"


def createNodeInfo(tx, name, isbundle, price, discount, reviews, release_date, URL):
    node = tx.run("create (g: Games {name: $name}) "
                  "set g.isbundle = $isbundle "
                  "set g.price = $price "
                  "set g.discount = $discount "
                  "set g.reviews = $reviews "
                  "set g.date = $release_date "
                  "set g.URL = $URL", name = name, isbundle = isbundle, price = price, discount = discount, reviews = reviews, release_date = release_date, URL = URL)
    return node

def addDatabaseInfo(uri, username, password, game_dict):

    
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
            try:
                session.write_transaction(createNodeInfo, game_name, game_bundle, game_price, game_discount, game_reviews, game_date, URL)
                
            except ex.ConstraintError:
                pass
        session.close()
    

def constructQuery(command_list):
    query = command_list[0] + " where "
    command_list.pop(0)
    for i, c in enumerate(command_list):
        if i == len(command_list) - 1:
            query = query + command_list[i] + "return properties(g) LIMIT 100"
            return query
        else:
            query = query + command_list[i] + " and "
        
    
        
            
def queryInfo(session, price_range, reviews, isdiscounted, isbundle):
    and_cnt = 0
    query_dict = dict()
    command_list = list()
    #Bundle recognition is a little fucked
    
    
    match = "match(g:Games) "
    command_list.append(match)

    
    if price_range == -1:
        lower_bound = 0
        upper_bound = 0
    else:
        lower_bound = price_range[0]
        upper_bound = price_range[1]
        price = "$lower_bound <= toFloat(substring( g.price, 1) ) <= $upper_bound "
        and_cnt += 1
        command_list.append(price)
    #Could use a little work on reviews to corerctly reocgnize input of "Very Positive" for example.
    if reviews != -1:
        rev = "$reviews in split(g.reviews, ' ') "
        and_cnt += 1
        command_list.append(rev)

        
    if isdiscounted != -1:
        discount = "g.discount <> '-0%' "
        and_cnt += 1
        command_list.append(discount)
    if isbundle != -1:
        isbundle = " g.isbundle = True "
        and_cnt += 1
        command_list.append(isbundle)

    and_cnt -= 1
    
    if and_cnt  > 0:
        final_query = constructQuery(command_list)
    elif and_cnt == 0:
        final_query = match + " where " + command_list[1] + " return properties(g) LIMIT 100"

       
    data = session.run(final_query, lower_bound = lower_bound, upper_bound = upper_bound , reviews = reviews, isbundle = isbundle)
    for record in data:
        item_list = list()
        
        properties = record.value()
        name = properties["name"]
        properties.pop("name")
        for game_prop, value in properties.items():
            item_list.append(value)
   
        query_dict[name] = tuple(item_list)

    return query_dict
        
def clearDatabase(uri, username, password):
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    with driver.session() as session:
        session.run("match (g:Games) delete g")
        session.close()
     
    
def updateDatabase(uri, username, password):
    clearDatabase(uri,username,password)
    bot = sb.SteamBot()
    bot.getGames("specials", 1,21)
    bot.getGames("topselling",1,21)
    bot.getGames("popularupcoming",1,21)
    bot.getGames("newandtrending",1,21)
    for game_dict in bot.getBotData():
        addDatabaseInfo(uri, username, password, game_dict)