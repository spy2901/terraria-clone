from globals import *
from world.sprite import *
from random import randint

class Item():
    def __init__(self, name:str = "default", quantity: int = 0) -> None:
        self.name = name 
        self.quantity = quantity
    def use(self, *args, **kwargs):
        pass
    def attack(self, *args, **kwargs):
        pass
    def __str__(self):
        return f'Name: {self.name} Quantity: {self.quantity}'

class BlockItem(Item): #placable item (block)
    def __init__(self, name: str, quantity: int = 0) -> None:
        super().__init__(name, quantity) 
    def use(self,player,position: tuple):
        if self.quantity > 0:
            items[self.name].use_type([player.group_list[group] for group in items[self.name].groups],player.textures[self.name],position,self.name)
            self.quantity -= 1
            if self.quantity <= 0:
                self.name = "default"
        else:
            self.name = 'default'

class ShortSwordItem(Item):
    def __init__(self, name: str = "default", quantity: int = 0) -> None:
        super().__init__(name, quantity)
    def use(self, player, position: tuple):
        print('using sword')
    
    def attack(self, player, target):
        target.kill()


class PickaxeItem(Item):
    def __init__(self, name: str = "default", quantity: int = 0) -> None:
        super().__init__(name, quantity)

    def use(self, player, position: tuple):
        print('using pickaxe')

    def attack(self, player, target):
        target.kill()


class ItemData:
    def __init__(self,name:str,quantity: int = 1, groups: list[str] = ['sprites', 'block_group'],use_type: Entity = Entity, item_type: Item = Item) -> None:
        self.name = name
        self.quantity = quantity
        self.groups = groups
        self.use_type = use_type
        self.item_type = item_type

items: dict[str, ItemData] = {
    'grass': ItemData('grass', quantity=1,item_type=BlockItem),
    'dirt': ItemData('dirt',quantity=1, item_type=BlockItem),
    'stone': ItemData('stone',quantity=1, item_type=BlockItem),
    'coal': ItemData('coal', quantity=randint(2,3),item_type=BlockItem),
    'gold': ItemData('gold', quantity=randint(1,3),item_type=BlockItem),
    'iron': ItemData('iron', quantity=randint(1,4),item_type=BlockItem),
    'wood': ItemData('iron', quantity=1,item_type=BlockItem),
    'leaf': ItemData('iron', quantity=1,item_type=BlockItem),
    'short_sword': ItemData('short_sword', item_type=ShortSwordItem),
    'wooden_pickaxe': ItemData('wooden_pickaxe', item_type=ShortSwordItem),
    'stone_pickaxe': ItemData('wooden_pickaxe', item_type=ShortSwordItem),
    'iron_pickaxe': ItemData('wooden_pickaxe', item_type=ShortSwordItem),
    'gold_pickaxe': ItemData('wooden_pickaxe', item_type=ShortSwordItem),
}
