import pygame  # For sprite handling and surface creation
from globals import TILESIZE  # Import TILESIZE or other constants you use for positioning
from world.sprite import Entity  # For creating the tree's individual blocks
from world.items import items  # For accessing block types like 'wood' and 'leaves'
import random  # If you're generating trees with some randomness

class Tree:
    def __init__(self, x, y, trunk_height, group_list, textures):
        self.x = x
        self.y = y
        self.trunk_height = trunk_height
        self.group_list = group_list
        self.textures = textures

        # Store references to the blocks that make up the tree
        self.trunk_blocks = []
        self.leaf_blocks = []

        # Generate the tree upon initialization
        self.generate_tree()

    def generate_tree(self):
        """Generates the trunk and leaves of the tree."""
        # Generate trunk
        for trunk_y in range(self.y, self.y + self.trunk_height):
            self.trunk_blocks.append(self.place_block(self.x, trunk_y-3, 'wood'))

        # Generate leaves
        # Adjust leaf placement to be relative to the top of the trunk
        for leaf_x in range(self.x - 2, self.x + 3):
            for leaf_y in range(self.y - self.trunk_height, self.y - self.trunk_height - 3, -1):
                distance = abs(leaf_x - self.x) + abs(leaf_y - (self.y - self.trunk_height))
                if distance < 3:
                    leaf_block = self.place_block(leaf_x, leaf_y, 'leaf', leaf=True)
                    self.leaf_blocks.append(leaf_block)

    def place_block(self, x, y, block_type, leaf=False):
        """Places a block at the given position."""
        use_type = items[block_type].use_type
        groups = [self.group_list[group] for group in items[block_type].groups]

        if leaf:
            # If it's a leaf, create a LeafBlock instance
            leaf_block = LeafBlock(groups, self.textures[block_type],
                                   (x * TILESIZE, y * TILESIZE), block_type, self.textures)
            return leaf_block
        else:
            # Regular block placement for trunk
            trunk_block = use_type(groups, self.textures[block_type],
                                   (x * TILESIZE, y * TILESIZE), block_type)
            return trunk_block

    def update(self):
        """Update the tree: manage leaf decay only if the tree is destroyed."""
        if self.is_destroyed:
            for leaf in self.leaf_blocks:
                leaf.increment_no_trunk_timer()  # Increment the timer for leaf decay
                leaf.update_visual()  # Update leaf visual based on health/timer

                if leaf.leaf_health <= 0:
                    print("destroyed leaf block")
                    leaf.kill()
                    self.leaf_blocks.remove(leaf)

    def destroy(self):
        """Destroy the tree and initiate leaf decay."""
        self.is_destroyed = True  # Set the flag to indicate the tree is destroyed



class LeafBlock(Entity):
    def __init__(self, groups, image, position, block_type, textures):
        super().__init__(groups, image, position, block_type)
        self.textures = textures
        self.leaf_health = 10  # Start with full health
        self.original_image = image.copy()  # Store the original image to modify it for decay

    def detect_nearby_trunk(self, trunk_blocks):
        """Check if there is a trunk nearby."""
        radius = 3  # Define the radius to check for trunk blocks
        for block in trunk_blocks:
            distance = abs(block.rect.x - self.rect.x) // TILESIZE + abs(block.rect.y - self.rect.y) // TILESIZE
            if distance <= radius:
                return True
        return False

    def update_visual(self):
        """Update the leaf's visual appearance based on its health."""
        # Fade the leaf's transparency as its health decreases
        transparency = max(0, int(255 * (self.leaf_health / 100)))  # Set transparency based on leaf health
        self.image = self.original_image.copy()
        self.image.fill((255, 255, 255, transparency), None, pygame.BLEND_RGBA_MULT)
