from globals import *

atlas_texture_data = {
    'grass': {'type': 'block','size': (TILESIZE, TILESIZE),'position':(0,0)},
    'dirt': {'type': 'block','size': (TILESIZE, TILESIZE),'position':(0,1)},
    'stone': {'type': 'block','size': (TILESIZE, TILESIZE),'position':(1,0)},
    'leaf': {'type': 'block','size': (TILESIZE, TILESIZE),'position':(2,0)},
    'wood': {'type': 'block','size': (TILESIZE, TILESIZE),'position':(1,1)},
    'coal': {'type': 'block','size': (TILESIZE, TILESIZE),'position':(2,1)},
    'gold': {'type': 'block','size': (TILESIZE, TILESIZE),'position':(3,2)},
    'iron': {'type': 'block','size': (TILESIZE, TILESIZE),'position':(2,3)},
}

solo_texture_data = {
    'player_static':{'type':'player','file_path':'res/player.png','size':(TILESIZE*2,TILESIZE*2)},
    'zombie_static':{'type':'enemy','file_path':'res/zombie.png','size':(TILESIZE*2,TILESIZE*2)},
    'short_sword':{'type':'weapon','file_path':'res/weapons/shortsword.png','size':(TILESIZE,TILESIZE)},
}   