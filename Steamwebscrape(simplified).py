import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
from bs4 import BeautifulSoup
#To do: Generalize Infograbing
#Fix reviews
#Fix bundle reading
#Implement Error handling
cookies = {'birthtime': '568022401'}

page = requests.get("https://store.steampowered.com/")
soup = BeautifulSoup(page.content, "html.parser")


tabs = dict()
tabs["topselling"] = ("tab_topsellers_content", "https://store.steampowered.com/search/?filter=topsellers&os=win", "https://store.steampowered.com/search/?os=win&filter=topsellers&page=")
tabs["newandtrending"] = "tab_newreleases_content"
tabs["popularupcoming"] = "tab_upcoming_content"
tabs["specials"] = ("tab_specials_content", "https://store.steampowered.com/search/?specials=1&os=win", "https://store.steampowered.com/search/?os=win&specials=1&page=")

#def getGamePageInfo(URL):
#    #Currently very broken
#    #Searches through a steam page and returns (reviews, release_date, developer)
#    #as a tuple
#    
#    game_page = requests.get(URL, cookies = cookies)
#    gp_soup = BeautifulSoup(game_page.content, "html.parser")
#    if "bundle" in URL:
#        main_panel = gp_soup.find(class_ = "details_block")
#        panel_items = main_panel.find_all('a')
#        developer = panel_items[2].get_text()
#        
#        reviews = "No reviews for bundles"
#        release_date = "No release date for bundles"
#        
#    else:
#        main_panel = gp_soup.find(class_ = "page_content_ctn")
#        #reviews = main_panel.find(class_ = "summary column").get_text().strip()
#        reviews = "Not yet implemented"
#        release_date = "Not yet implemented"
#        #release_date = main_panel.find(class_ = "date").get_text().strip()
#        developer = "No"
#        #developer = main_panel.find(id = "developers_list").get_text().strip()
#    return (reviews, release_date, developer)


def getAllGamesInfo(game_container):
    #Returns tuple of information 
    #(Bundle status, price, discount percent, tags, URL)
    
    game_date = game_container.find(class_ = "search_released")
    if game_date is None:
        game_date = "Not yet released"
    else:
        game_date = game_date.get_text()
        
    #game_reviews = game_container.find(class_ = "search_review_summary")
    game_reviews = "Not yet implemented"
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
        
    
    
    return (game_bundle, game_price, game_discount, game_date, URL)
        


def getAllGames(game_category, upper_bound = 1):
    game_dict = dict()
    URL = tabs[game_category][1]
    nth_page = tabs[game_category][2]
    initial_page = requests.get(URL)
    initial_soup = BeautifulSoup(initial_page.content, "html.parser")
    
    page_number = 1
    
    while(page_number <= upper_bound):
        if page_number == 1:
            #Pulls stuff from initial page and creates game containers
            search_result_container = initial_soup.find(id  = "search_result_container")
            game_containers = search_result_container.find_all(class_ = "search_result_row")
            
            #Iterates through the page's games
            for container in game_containers:
                game_name = container.find(class_ = "title").get_text()
                game_tuple = getAllGamesInfo(container)
                game_dict[game_name] = game_tuple
                
                
            page_number += 1
            
        else:
            #Check to see if page is valid
            #Pulls stuff from nth page
            nth_req =  requests.get(nth_page + str(page_number))
            nth_soup = BeautifulSoup(nth_req.content, "html.parser")
            search_result_container = nth_soup.find(id  = "search_result_container")
            search_test = search_result_container.get_text().strip()
            
            
            if "No results were returned for that query." in search_test:
                #This page does not contain games
                break
                
            else:
                #This page contains games
                game_containers = search_result_container.find_all(class_ = "search_result_row")
                for container in game_containers:
                        
                    game_name = container.find(class_ = "title").get_text()
                    game_tuple = getAllGamesInfo(container)
                    game_dict[game_name] = game_tuple
                    
                page_number += 1

    return game_dict


def printTabInfo(tab_dictionary):
    #Prints the dictionary of games and information    
    tab_dataframe =pd.DataFrame.from_dict(tab_dictionary)

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(tab_dataframe)
    
        
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
    
    
   
    
def getFrontPageGames(tab_id):
    #Iterates through a given steam tab and extracts information about the games
    info_dict = dict()
    
    info = soup.find(id = tab_id)
    container_list = info.find_all(class_ = "tab_item")
    
    for item in container_list:
        game_name = item.find(class_ = "tab_item_name").get_text()
        info_tup = getFrontPageInfo(item)
        info_dict[game_name] = info_tup
    
    return info_dict
    
    #discount_percent = top_sellers.find_all(class_= "discount_pct")
    #print(discount_percent)
   
    #print(top_sellers.prettify())
    
    
def main():
#   tab_info = getFrontPageGames(tabs["specials"][0])
#   printTabInfo(tab_info)
    Specials = getAllGames("topselling")
    printTabInfo(Specials)
    
   


if __name__ == "__main__":
    main()

