import fandom
from crafting_item import CraftingItem
import json
from bs4 import BeautifulSoup
from treelib import Tree

fandom.set_wiki('calamitymod')

cwiki = True

def flip_wiki():
    global cwiki
    if cwiki:
        fandom.set_wiki('terraria')
    else:
        fandom.set_wiki('calamitymod')
    cwiki = not cwiki

def get_recipe_prettified(itemname):
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
                recipe[name] = {}
                try:
                    quantity = int(td[2].contents[0])
                    recipe[name]['quantity'] = quantity
                except:
                    recipe[name]['quantity'] = 1  
                recipe[name]['recipe'] = get_recipe(name)
                if not recipe[name]['recipe']:
                    recipe[name].pop('recipe')
            elif mode == 'res':
                continue
        return recipe
    final_recipe = {
        itemname: {
            'quantity': 1,
            'recipe': get_recipe(itemname)
        }
    }
    return final_recipe





def get_recipe(itemname):
    def get_recipe(itemname, quantity=1):
        recipe = {}
        recipe['name'] = itemname
        recipe['quantity'] = quantity
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
                recipe['station'] = tr.find('a')['title']
                recipe['recipe'] = []
            elif mode == 'ing':
                td = tr.find_all('td')
                name = td[0].find('a')['title'] # ingredient name
                quantity = int(td[2].contents[0])
                recipe['recipe'].append(get_recipe(name, quantity))
            elif mode == 'res':
                continue
        return recipe

    return get_recipe(itemname)






def create_tree_from_recipe(recipe):
    tree = Tree()
    root_init = False
    keys = list(recipe.keys())

    def add_nodes(layer, parentname):
        nonlocal root_init
        for item in layer:
            if item == 'Station':
                continue
            if 'recipe' in layer[item]:
                if root_init:
                    node = tree.create_node(item, parent=parentname, data=CraftingItem(item, layer[item]['quantity'], layer[item]['recipe']['Station']))
                else:
                    node = tree.create_node(item, data=CraftingItem(item, layer[item]['quantity'], layer[item]['recipe']['Station']))
                    root_init = True
                add_nodes(layer[item]['recipe'], node.identifier)
            else:
                tree.create_node(item, parent=parentname, data=CraftingItem(item, layer[item]['quantity']))




    add_nodes(recipe, keys[0])

    tree.show(data_property='printname')


print(json.dumps(get_recipe('Fallen Paladin\'s Hammer'), indent=4))
