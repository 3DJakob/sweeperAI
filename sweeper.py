import pygame

pygame.init()
font = pygame.font.Font('font.otf', 25)

GRIDX = 20
GRIDY = 20
TILESIZE = 30
SPEED = 60

class SweeperGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((GRIDX * TILESIZE, GRIDY * TILESIZE))
        self.map = self._generateMap()
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

        self._drawTile(0, 0)

        # draw tiles from map
        for x in range(GRIDX):
            for y in range(GRIDY):
                self._drawTile(x, y, "0")


        pygame.display.flip()
          
    def _drawTile(self, x, y, text="0"):
        # draw tile at x, y with size TILESIZE
        pygame.draw.rect(self.screen, (255, 255, 255), (x * TILESIZE, y * TILESIZE, TILESIZE, TILESIZE), 1)
        # draw a number in the middle of the tile
        text = font.render(text, True, (255, 255, 255))
        # reduce font size
        self.screen.blit(text, (x * TILESIZE + TILESIZE / 2 - text.get_width() // 2, y * TILESIZE + TILESIZE / 2 - text.get_height() // 2))

    def _generateMap(self):
        # create array with size GRIDX * GRIDY
        map = [[0 for x in range(GRIDX)] for y in range(GRIDY)]
        print(map)
        return map





if __name__ == '__main__':
    game = SweeperGame()
    game.run()
    pygame.quit()