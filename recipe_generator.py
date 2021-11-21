import fandom
from crafting_item import CraftingItem
import json
from bs4 import BeautifulSoup
from treelib import Tree
import uuid
from re import sub

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

def create_tree_from_recipe(recipe):
    tree = Tree()
    #create root node
    if 'station' in recipe:
        tree.create_node(recipe['name'], identifier=recipe['name'], data=CraftingItem(recipe['name'], 1, recipe['station']))
    else:
        tree.create_node(recipe['name'], identifier=recipe['name'], data=CraftingItem(recipe['name'], 1))

    def add_nodes(layer, parentname):
        for item in layer:
            if 'station' in item:
                node = tree.create_node(item['name'], parent=parentname, data=CraftingItem(item['name'], item['quantity'], item['station']))
            else:
                node = tree.create_node(item['name'], parent=parentname, data=CraftingItem(item['name'], item['quantity']))
            
            if 'recipe' in item:
                add_nodes(item['recipe'], node.identifier)

    if 'recipe' in recipe:
        add_nodes(recipe['recipe'], recipe['name'])

#    tree.show(data_property='printname')
    return tree

# use get_recipe to 
def create_wikitree_from_recipe(recipe):
    tree = create_tree_from_recipe(recipe)
    properties = '\n'
    working_wikitree = ''
    def create_id(item):
        return str(uuid.uuid4())[:4] + sub('[^A-Z]', '', item)

    def add_layer(layeritems):
        nonlocal properties, working_wikitree
        layer_text = ''
        for node in layeritems:
            item = tree[node].data
            item_name = item.get_name()
            item_id = create_id(item_name)
            if item.get_quantity() != 1:
                properties += '|%s_cols=1\n|%s_rows=1\n|%s={{item|%s}} x %d\n' %(item_id, item_id, item_id, item_name, item.get_quantity())
            else:
                properties += '|%s_cols=1\n|%s_rows=1\n|%s={{item|%s}}\n' %(item_id, item_id, item_id, item_name)
            layer_text += '|_|' +  item_id 
        working_wikitree = layer_text + '|_|#\n' + working_wikitree 

    depth = 0
    while depth <= tree.depth():
        layeritems = []
        for node in tree.expand_tree(mode=Tree.WIDTH):
            if tree.depth(node) == depth:
                layeritems.append(node)
        add_layer(layeritems)
        depth += 1

    return '{{diagram\n' + working_wikitree + properties + "}}"
    


def create_wikitree_from_item(item):
    return create_wikitree_from_recipe(get_recipe(item))


#print(json.dumps(get_recipe('Fallen Paladin\'s Hammer'), indent=4))
recipe = {
    "name": "Fallen Paladin's Hammer",
    "quantity": 1,
    "station": "Mythril Anvil",
    "recipe": [
        {
            "name": "Paladin's Hammer",
            "quantity": 1
        },
        {
            "name": "Pwnagehammer",
            "quantity": 1,
            "station": "Mythril Anvil",
            "recipe": [
                {
                    "name": "Pwnhammer",
                    "quantity": 1
                },
                {
                    "name": "Soul of Might",
                    "quantity": 3
                },
                {
                    "name": "Soul of Fright",
                    "quantity": 3
                },
                {
                    "name": "Soul of Sight",
                    "quantity": 3
                },
                {
                    "name": "Hallowed Bar",
                    "quantity": 7
                }
            ]
        },
        {
            "name": "Ashes of Calamity",
            "quantity": 5
        },
        {
            "name": "Core of Chaos",
            "quantity": 5,
            "station": "Mythril Anvil",
            "recipe": [
                {
                    "name": "Essence of Chaos",
                    "quantity": 1
                },
                {
                    "name": "Ectoplasm",
                    "quantity": 1
                }
            ]
        },
        {
            "name": "Scoria Bar",
            "quantity": 5,
            "station": "Adamantite Forge",
            "recipe": [
                {
                    "name": "Scoria Ore",
                    "quantity": 5
                }
            ]
        }
    ]
}


print(create_wikitree_from_recipe(recipe))
#create_tree_from_recipe(recipe)
