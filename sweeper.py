import pygame
import random

pygame.init()
font = pygame.font.Font('font.otf', 25)

GRIDX = 15
GRIDY = 15
TILESIZE = 30
SPEED = 60
NUMBEROFMINES = 40

class SweeperGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((GRIDX * TILESIZE, GRIDY * TILESIZE))
        self.map = self._generateMap()
        self.userMap = self._generateUserMap()
        self.clock = pygame.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        pass

    def draw(self):
        self.screen.fill((0, 0, 0))
        # draw tiles from map
        for x in range(GRIDX):
            for y in range(GRIDY):
                self._drawTile(x, y, self.map[y][x])


        pygame.display.flip()
          
    def _drawTile(self, x, y, text=0):
        # draw tile at x, y with size TILESIZE
        if text == 9:
            text = 'B'

        pygame.draw.rect(self.screen, (255, 255, 255), (x * TILESIZE, y * TILESIZE, TILESIZE, TILESIZE), 1)
        textElement = font.render(str(text), True, (255, 255, 255))
        self.screen.blit(textElement, (x * TILESIZE + TILESIZE / 2 - textElement.get_width() // 2, y * TILESIZE + TILESIZE / 2 - textElement.get_height() // 2))

    def _calculateTileNumber(self, x, y, map):
        number = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if x + i < 0 or x + i >= GRIDX or y + j < 0 or y + j >= GRIDY:
                    continue
                if map[y + j][x + i] == 9:
                    number += 1
        return number

    def _generateMap(self):
        # create array with size GRIDX * GRIDY
        map = [[0 for x in range(GRIDX)] for y in range(GRIDY)]

        # place mines
        for i in range(NUMBEROFMINES):
            x = random.randint(0, GRIDX - 1)
            y = random.randint(0, GRIDY - 1)
            map[y][x] = 9

        # calculate numbers
        for x in range(GRIDX):
            for y in range(GRIDY):
                if map[y][x] == 9:
                    continue
                map[y][x] = self._calculateTileNumber(x, y, map)

        print(map)
        return map
    
    def _generateUserMap(self):
        # The user map is the map that the user/AI sees
        # 10 = unexplored
        map = [[10 for x in range(GRIDX)] for y in range(GRIDY)]
        return map





if __name__ == '__main__':
    game = SweeperGame()
    game.run()
    pygame.quit()