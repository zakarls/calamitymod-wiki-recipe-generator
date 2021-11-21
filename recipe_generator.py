import fandom
import json
from bs4 import BeautifulSoup
from treelib import Node, Tree

fandom.set_wiki('calamitymod')

cwiki = True
#recipe_section = item_page.section("Recipe")
#print(recipe_section)
#print(json.dumps(item_page.content, indent=4))

def flip_wiki():
    global cwiki
    if cwiki:
        fandom.set_wiki('terraria')
    else:
        fandom.set_wiki('calamitymod')
    cwiki = not cwiki

def get_recipe(itemname):
    def get_recipe(itemname):
        recipe = {}
        try:
            item_page = fandom.page(title=itemname)
        except (fandom.error.PageError, KeyError):
            flip_wiki()
            try:
                item_page = fandom.page(title=itemname)
            except fandom.error.PageError:
                return recipe
        sections = item_page.sections
        if "Recipe" not in sections:
            return recipe
        html = BeautifulSoup(item_page.html, 'html.parser')

        recipe_table = ''
        for table in html.find_all('table'):
            if 'Crafting Station' in table.find_next('tr').find_next('th').contents:
                recipe_table = table
                break
        
        mode = ''
        for tr in recipe_table.find_all('tr'):
            if tr.find('th') is not None:
                if tr.find('th').find('b') is None:
                    content = tr.find('th').contents[0]
                else:
                    content = tr.find('th').find('b').contents[0]
                if content == 'Crafting Station':
                    mode = 'cs'
                elif content == 'Ingredient(s)':
                    mode = 'ing'
                elif content == 'Result':
                    mode = 'res'
                continue
            if mode == 'cs':
                recipe['Station'] = tr.find('a')['title']
            elif mode == 'ing':
                td = tr.find_all('td')
                name = td[0].find('a')['title']
                #print("ItemName: %s ; FoundName: %s" %(itemname, name))
                recipe[name] = get_recipe(name)
                try:
                    quantity = int(td[2].contents[0])
                    recipe[name]['quantity'] = quantity
                except:
                    recipe[name]['quantity'] = 1
            elif mode == 'res':
                continue
        return recipe
    return {
        itemname: get_recipe(itemname)
    }


def create_tree_from_recipe(recipe):
    tree = Tree()
    def add_node():
        for layer in recipe:
            pass


#get_recipe("Fallen Paladin\'s Hammer")
print(json.dumps(get_recipe('Triactis\' True Paladinian Mage-Hammer of Might'), indent=4))
#print(json.dumps(get_recipe('Zenith'), indent=4))
