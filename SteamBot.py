import requests
import pandas as pd
import utility_functions as uf
#NEed to handle category dict and streamlining names correctly


from bs4 import BeautifulSoup

class Bot:
    def __init__(self):
        pass
    
class SteamBot(Bot):
    def __init__(self):
        self._data = list()
        self.category_dict = dict()
        self.category_dict["topselling"] = ("tab_topsellers_content", "https://store.steampowered.com/search/?filter=topsellers&os=win", "https://store.steampowered.com/search/?os=win&filter=topsellers&page=")
        self.category_dict["newandtrending"] = ("tab_newreleases_content", "https://store.steampowered.com/search/?filter=popularnew&sort_by=Released_DESC&os=win", "https://store.steampowered.com/search/?sort_by=Released_DESC&os=win&filter=popularnew&page=")
        self.category_dict["popularupcoming"] = ("tab_upcoming_content", "https://store.steampowered.com/search/?filter=popularcomingsoon&os=win", "https://store.steampowered.com/search/?os=win&filter=popularcomingsoon&page=")
        self.category_dict["specials"] = ("tab_specials_content", "https://store.steampowered.com/search/?specials=1&os=win", "https://store.steampowered.com/search/?os=win&specials=1&page=")
        self.page = requests.get("https://store.steampowered.com/")
        self.soup = BeautifulSoup(self.page.content, "html.parser")
        
    def getFrontPageGames(self, tab_name):
        #Iterates through a given steam tab and extracts information about the games
        #Should I store the tab_name in the tuple as well?
        info_dict = dict()
        tab_name = uf.getValidName(tab_name)
        if tab_name == "error":
            raise Exception ("The input given for the game category is invalid.")
            
        tab_id = self.category_dict[tab_name][0]
        
        info = self.soup.find(id = tab_id)
        container_list = info.find_all(class_ = "tab_item")
        
        for item in container_list:
            game_name = item.find(class_ = "tab_item_name").get_text()
            info_tup = uf.getFrontPageInfo(item)
            info_dict[game_name] = info_tup
        
        self._data.append(info_dict)
        
    def getGames(self, game_category, lower_bound = 1, upper_bound = 1):
        
        game_category = uf.getValidName(game_category)
        if game_category == "error":
            raise Exception ("The input given for the game category is invalid.")
        if lower_bound < 0 or upper_bound < 0:
            raise Exception ("The bounds must be at least 1.")
        
        game_dict = dict()
        URL = self.category_dict[game_category][1]
        nth_page = self.category_dict[game_category][2]
        initial_page = requests.get(URL)
        initial_soup = BeautifulSoup(initial_page.content, "html.parser")
        
        page_number = lower_bound
        
        while(page_number <= upper_bound):
            if page_number == 1:
                #Pulls stuff from initial page and creates game containers
                search_result_container = initial_soup.find(id  = "search_result_container")
                game_containers = search_result_container.find_all(class_ = "search_result_row")
                
                #Iterates through the page's games
                for container in game_containers:
                    game_name = container.find(class_ = "title").get_text()
                    game_tuple = uf.getGamesInfo(container)
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
                        game_tuple = uf.getGamesInfo(container)
                        game_dict[game_name] = game_tuple
                        
                    page_number += 1
    
        self._data.append(game_dict)
        
    def printDataInfo(self, upper_bound = 0):
        #Shouldn't exactly work like this. Rethink this funciton.
        #Prints the dictionary of games and information  

        if upper_bound == 0:
            dataframe = pd.DataFrame.from_dict(self._data[0])
            with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                print(dataframe)
        elif upper_bound <= len(self._data):
            
            for i in range(upper_bound):
                dataframe = pd.DataFrame.from_dict(self._data[i])
                with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                    print(dataframe)