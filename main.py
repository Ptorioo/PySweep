import pygame
from pygame.locals import *
from random import shuffle

pygame.init()
font = pygame.font.SysFont("calibri", 14)
bigfont = pygame.font.SysFont("calibri", 40)
colors = {'white': (255,255,255), 'black': (0, 0, 0), 'grey': (169, 169, 169), 'red': (255, 0, 0), 'orange': (255, 165, 0), 'brickred': (178, 34, 34), 'blue': (0, 0, 205)}
size = 20

class Tile(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.border = pygame.Surface((size, size))
		self.inside = pygame.Surface((size - 2, size - 2))
		self.image = pygame.Surface((size, size))
		
		self.border.fill(colors['black'])
		self.inside.fill( colors['grey'])
		self.image.blit(self.border,(0, 0))
		self.image.blit(self.inside,(2, 2))
		self.rect = self.image.get_rect()
		self.checked, self.isBomb, self.flagged = False, False, False
		self.num = 0
		
	def Check(self):
		if not self.checked:
			if (self.isBomb):
				self.inside.fill( colors['red'])
			else:
				self.inside.fill(colors['white'])
				if (self.num != 0):
					numtext = font.render(str(self.num), True, colors['black'])
					self.inside.blit(numtext,(self.rect.width / 4,numtext.get_height() / 4))
			self.image.blit(self.inside,(2, 2))
			self.checked = True
		
	def Flag(self):
		if not self.checked:
			if self.flagged:
				self.flagged = False
				self.inside.fill(colors['grey'])
				self.image.blit(self.inside, (2, 2))
				return False
			else:
				self.flagged = True
				flag = pygame.Surface((self.inside.get_width() - 4, self.inside.get_height() - 4))
				flag.fill( colors['orange'])
				self.inside.blit(flag,(2, 2))
				self.image.blit(self.inside,(2, 2))
				return True
		else:
			return False

class Grid(pygame.sprite.Group):
	def __init__(self):
		pygame.sprite.Group.__init__(self)
		self.dimensions = (16, 16)
		self.bombs = 40
		test = list(range(self.dimensions[0] * self.dimensions[1]))
		shuffle(test)
		for i in range(self.dimensions[0]):
			for j in range(self.dimensions[1]):
				temp = Tile()
				temp.rect.topleft = (i * size, j * size)
				if (test.pop() < self.bombs):
					temp.isBomb = True
				else:
					temp.isBomb = False
				self.add(temp)
		
		for t in self.sprites():
			if t.isBomb == False:
				temp = pygame.sprite.Sprite()
				temp.rect = t.rect.copy()
				temp.rect.inflate_ip(2, 2)
				intersect = pygame.sprite.spritecollide(temp, self, False)
				for i in intersect:
					if i.isBomb:
						t.num += 1
				
def main():
    grid = Grid()

    flags, correctFlags = 0, 0

    resolution = (grid.dimensions[0] * size + 2, grid.dimensions[1] * size + 32)
    screen = pygame.display.set_mode(resolution)
    info = pygame.Surface((grid.dimensions[0] * size + 2, 30))
    info.fill(colors['white'])

    clock = pygame.time.Clock()
    gamestart, lbuttonpress, rbuttonpress, won, lost = False, False, False, False, False
    lose_time = None

    pygame.mouse.set_visible(True)

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0] and not lbuttonpress:
                    lbuttonpress = True
                if pygame.mouse.get_pressed()[2] and not rbuttonpress:
                    rbuttonpress = True
            elif event.type == MOUSEBUTTONUP:
                if not pygame.mouse.get_pressed()[0] and lbuttonpress:
                    if not gamestart:
                        gamestart = True
                        starttime = pygame.time.get_ticks()

                    lbuttonpress = False
                    mousesprite = pygame.sprite.Sprite()

                    if won or lost:
                        grid = Grid()
                        flags, correctFlags = 0, 0
                        starttime = pygame.time.get_ticks()
                        won, lost = False, False

                    mousesprite.rect = pygame.Rect(pygame.mouse.get_pos(), (1, 1))
                    mintersect = pygame.sprite.spritecollide(mousesprite, grid, False)

                    if mintersect:
                        for m in mintersect:
                            m.Check()
                            if m.isBomb:
                                lost = True
                                lose_time = pygame.time.get_ticks()
                            elif not m.isBomb and m.num == 0:
                                temp = pygame.sprite.Sprite()
                                temp.rect = m.rect.copy()
                                temp.rect.inflate_ip(2, 2)
                                rintersect = pygame.sprite.spritecollide(temp, grid, False)
                                for r in rintersect:
                                    if not r.checked and not any(item.rect == r.rect for item in mintersect):
                                        mintersect.append(r)

                if not pygame.mouse.get_pressed()[2] and rbuttonpress:
                    rbuttonpress = False
                    mousesprite = pygame.sprite.Sprite()
                    mousesprite.rect = pygame.Rect(pygame.mouse.get_pos(), (1, 1))
                    intersect = pygame.sprite.spritecollide(mousesprite, grid, False)

                    if intersect:
                        for i in intersect:
                            if i.Flag():
                                flags += 1
                                if i.isBomb:
                                    correctFlags += 1
                                    if correctFlags == grid.bombs:
                                        won = True
                            else:
                                flags -= 1
                                if i.isBomb:
                                    correctFlags -= 1

        grid.draw(screen)
        screen.blit(info, (0, grid.dimensions[0] * size + 3))

        if not won and not lost:
            if gamestart:
                currenttime = int((pygame.time.get_ticks() - starttime) / 1000)
                info.fill(colors['white'])
                timetext = font.render('Time: ' + str(currenttime), True, colors['black'])
                info.blit(timetext, (0, 0))
                flagstext = font.render('Flags: ' + str(flags), True, colors['black'])
                info.blit(flagstext, (resolution[0] / 2, 0))
        else:
            if won:
                endtext = bigfont.render('You win!', True, colors['blue'])
            else:
                endtext = bigfont.render('You lose!', True, colors['brickred'])
            screen.blit(endtext, (resolution[0] / 2 - endtext.get_width() / 2, (resolution[1] - 30) / 2 - endtext.get_height() / 2))

            if lost and lose_time and pygame.time.get_ticks() - lose_time > 1000:
                grid = Grid()
                flags, correctFlags = 0, 0
                starttime = pygame.time.get_ticks()
                won, lost = False, False
                lose_time = None

        pygame.display.flip()
	
if __name__ == '__main__':
	main()