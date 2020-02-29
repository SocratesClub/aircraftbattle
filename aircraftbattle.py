#导入模块
import pygame
import random
from pygame.locals import *
from os import path

#######################################基本参数配置#######################################

#获取图片库和声音库路径
img_dir = path.join(path.dirname(__file__),'pic')
sound_folder = path.join(path.dirname(__file__),'sounds')

#定义游戏窗口、玩家血量条尺寸，游戏运行速度、炮火持续时间等参数
WIDTH = 480
HEIGHT = 600
FPS = 60
POWERUP_TIME = 5000
BAR_LENGTH = 100
BAR_HEIGHT = 10

#定义白、黑、红、绿、蓝、黄的RGB参数 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

#初始化pygame模块，创建游戏窗口、游戏窗口命名、创建跟踪时间对象
pygame.init()
pygame.mixer.init()  #初始化音效
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Aircraft Battle")
clock = pygame.time.Clock()

#定义文本字体
font_name = pygame.font.match_font('arial')

#######################################加载图片#######################################

#加载游戏进行中背景图片
background = pygame.image.load(path.join(img_dir,'starfield.png')).convert()
background = pygame.transform.scale(background,(WIDTH,1536))
height = -936

#加载玩家图片
player_img = pygame.image.load(path.join(img_dir,'player.png')).convert()
player_mini_img = pygame.transform.scale(player_img,(25, 19))
player_mini_img.set_colorkey(BLACK)

#加载玩家炮弹、导弹图片
bullet_img = pygame.image.load(path.join(img_dir,'bullet.png')).convert()
missile_img = pygame.image.load(path.join(img_dir,'missile.png')).convert_alpha()

#加载敌机炮弹图片
enemies_bullet_img = pygame.image.load(path.join(img_dir,'enemies_bullet.png')).convert()

#加载盾牌、闪电图片
powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'shield.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt.png')).convert()

#加载敌机和火山石图片
enemies_images = []
lava_images = []
#敌机
enemies_list = [
    'enemies1.png',
    'enemies2.png',
    'enemies3.png'
]
#火山石
lava_list = [
    'lava_med.png',
    'lava_small1.png',
    'lava_small2.png',
    'lava_tiny.png'
]
for image in enemies_list:
    enemies_img = pygame.image.load(path.join(img_dir,image)).convert()
    enemies_img = pygame.transform.scale(enemies_img,(80, 60))
    enemies_images.append(enemies_img)
for image in lava_list:
    lava_images.append(pygame.image.load(path.join(img_dir,image)).convert())

#加载爆炸图片
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    #敌机、火山石爆炸
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir,filename)).convert()
    img.set_colorkey(BLACK)
    #大爆炸    
    img_lg = pygame.transform.scale(img,(75,75))
    explosion_anim['lg'].append(img_lg)
    #小爆炸
    img_sm = pygame.transform.scale(img,(32,32))
    explosion_anim['sm'].append(img_sm)
    #玩家爆炸
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir,filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)

#######################################加载声音#######################################

#加载炮弹、导弹发射声音
shooting_sound = pygame.mixer.Sound(path.join(sound_folder,'pew.wav'))
missile_sound = pygame.mixer.Sound(path.join(sound_folder,'rocket.ogg'))

#加载敌机、火山石爆炸声音
expl_sounds = []
for sound in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(sound_folder,sound)))
#调低音量
pygame.mixer.music.set_volume(0.2)

#加载玩家爆炸声音
player_die_sound = pygame.mixer.Sound(path.join(sound_folder,'rumble1.ogg'))

#######################################函数区#######################################

#游戏初始界面和准备开始界面函数
def main_menu():
    global screen
    #加载游戏初始界面背景音乐
    menu_song = pygame.mixer.music.load(path.join(sound_folder,"menu.ogg"))
    #循环播放
    pygame.mixer.music.play(-1)
    #加载游戏初始界面背景图片
    title = pygame.image.load(path.join(img_dir,"main.png")).convert()
    title = pygame.transform.scale(title,(WIDTH, HEIGHT),screen)
    screen.blit(title,(0,0))
    pygame.display.update()
    #检测玩家操作事件
    while True:
        ev = pygame.event.poll()
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                break
        elif ev.type == pygame.QUIT:
                pygame.quit()
                quit()
        else:
            draw_text(screen, "Press [ENTER] To Begin", 30, WIDTH/2, HEIGHT/2)
            draw_text(screen, "[A] ←  [S] ↓  [D] →  [W] ↑", 30, WIDTH/2, 2*HEIGHT/3) 
            draw_text(screen, "[Space] fire", 30, WIDTH/2, 3*HEIGHT/4)           
            pygame.display.update()
    #加载准备声音
    ready = pygame.mixer.Sound(path.join(sound_folder,'getready.ogg'))
    ready.play()
    #加载准备开始界面背景颜色和文本
    screen.fill(BLACK)
    draw_text(screen, "GET READY!", 40, WIDTH/2, HEIGHT/3)
    pygame.display.update()

#设置文本属性函数
def draw_text(surf,text,size,x,y):
    #定义文本参数
    font = pygame.font.Font(font_name,size)
    text_surface = font.render(text,True,WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x,y)
    surf.blit(text_surface,text_rect)

#设置玩家血量条属性函数
def draw_shield_bar(surf,x,y,pct):
    pct = max(pct,0)
    fill = (pct/100)*BAR_LENGTH
    outline_rect = pygame.Rect(x,y,BAR_LENGTH,BAR_HEIGHT)
    fill_rect = pygame.Rect(x,y,fill,BAR_HEIGHT)
    pygame.draw.rect(surf,GREEN,fill_rect)
    pygame.draw.rect(surf,WHITE,outline_rect,2)

#设置玩家生命数量属性函数
def draw_lives(surf,x,y,lives,img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x+30*i
        img_rect.y = y
        surf.blit(img,img_rect)

#添加敌机函数
def newmob():
    mob_element = Mob()
    all_sprites.add(mob_element)
    mobs.add(mob_element)

#添加火山石函数
def newlava():
    lava_element = Lava()
    all_sprites.add(lava_element)
    lavas.add(lava_element)

#######################################类区#######################################

class Explosion(pygame.sprite.Sprite):
    '''创建爆炸类'''
    def __init__(self,center,size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0 
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

    def update(self):        
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

class Player(pygame.sprite.Sprite):
    '''创建玩家类'''
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img,(50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT-10
        self.speedx = 0
        self.speedy = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_timer = pygame.time.get_ticks()

    def update(self):
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME: 
            self.power -= 1
            self.power_time = pygame.time.get_ticks()
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH/2
            self.rect.bottom = HEIGHT-30
        self.speedx = 0
        self.speedy = 0
        #方向控制：A控制左、D控制右、W控制上、S控制下、A+W控制左上、A+S控制左下、D+W控制右上、D+S控制右下
        keystate = pygame.key.get_pressed()
        if keystate[K_a]:
            self.speedx = -5
        if keystate[K_d]:
            self.speedx = 5
        if keystate[K_w]:
            self.speedy = -5
        if keystate[K_s]:
            self.speedy = 5
        #发射控制：空格
        if keystate[pygame.K_SPACE]:
            self.shoot()
        #设置玩家移动边界
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 10:
            self.rect.top = 10
        if self.rect.bottom > HEIGHT-10:
            self.rect.bottom = HEIGHT-10
        self.rect.x += self.speedx
        self.rect.y += self.speedy

    def shoot(self):
        now = pygame.time.get_ticks()
        if now-self.last_shot > self.shoot_delay:
            self.last_shot = now
            #单火力
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shooting_sound.play()
            #双火力
            if self.power == 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shooting_sound.play()
            #三火力
            if self.power >= 3:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                missile1 = Missile(self.rect.centerx, self.rect.top) # 导弹
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                all_sprites.add(missile1)
                bullets.add(bullet1)
                bullets.add(bullet2)
                bullets.add(missile1)
                shooting_sound.play()
                missile_sound.play()

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2, HEIGHT+200)

class Mob(pygame.sprite.Sprite):
    '''创建敌机类'''
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(enemies_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width*.90/2)
        self.rect.x = random.randrange(0, WIDTH-self.rect.width)
        self.rect.y = random.randrange(-150,-100)       
        self.speedy = random.randrange(5,10)
        self.speedx = random.randrange(-3,3)
        self.shoot_delay = 1000
        self.last_shot = pygame.time.get_ticks()        

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if random.randrange(10) >= 6:
            self.enemies_shoot()        
        if (self.rect.top > HEIGHT+10) or (self.rect.left < -25) or (self.rect.right > WIDTH+20):
            self.rect.x = random.randrange(0,WIDTH-self.rect.width)
            self.rect.y = random.randrange(-100,-40)
            self.speedy = random.randrange(1,8)
    
    def enemies_shoot(self):
        now = pygame.time.get_ticks()
        if now-self.last_shot > self.shoot_delay:
            self.last_shot = now
            enemies_bullet = EnemiesBullet(self.rect.centerx, self.rect.bottom)
            all_sprites.add(enemies_bullet)
            enemies_bullets.add(enemies_bullet)
            shooting_sound.play()

class Lava(pygame.sprite.Sprite):
    '''创建火山石类'''
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(lava_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width*.90/2)
        self.rect.x = random.randrange(0, WIDTH-self.rect.width)
        self.rect.y = random.randrange(-150,-100)       
        self.speedy = random.randrange(5,10)
        self.speedx = random.randrange(-3,3)
        self.rotation = 0
        self.rotation_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    #添加火山石旋转效果
    def rotate(self):
        time_now = pygame.time.get_ticks()
        if time_now-self.last_update > 50:
            self.last_update = time_now
            self.rotation = (self.rotation+self.rotation_speed)%360 
            new_image = pygame.transform.rotate(self.image_orig,self.rotation)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center                

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy               
        if (self.rect.top > HEIGHT+10) or (self.rect.left < -25) or (self.rect.right > WIDTH+20):
            self.rect.x = random.randrange(0,WIDTH-self.rect.width)
            self.rect.y = random.randrange(-100,-40)
            self.speedy = random.randrange(1,8)       

class Bullet(pygame.sprite.Sprite):
    '''创建玩家炮弹类'''
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y 
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class EnemiesBullet(pygame.sprite.Sprite):
    '''创建敌机炮弹类'''
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = enemies_bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.top = y 
        self.rect.centerx = x
        self.speedy = 10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > 600:
            self.kill()

class Missile(pygame.sprite.Sprite):
    '''创建导弹类'''
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = missile_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Pow(pygame.sprite.Sprite):
    '''创建补给类'''
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 4

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

#######################################主循环#######################################

#定义游戏开始界面标识
running = True
menu_display = True

while running:
    if menu_display:
        main_menu()
        pygame.time.wait(3000)
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path.join(sound_folder,'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
        pygame.mixer.music.play(-1)
        menu_display = False

        all_sprites = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)        
        mobs = pygame.sprite.Group()
        for i in range(4):
            newmob()
        lavas = pygame.sprite.Group()
        for i in range(4): 
            newlava()
        bullets = pygame.sprite.Group()
        enemies_bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()

        score = 0   

    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    all_sprites.update()
    
    #敌机与玩家炮弹碰撞检测
    hits = pygame.sprite.groupcollide(mobs,bullets,True,True)    
    for hit in hits:
        score += 50-hit.radius
        random.choice(expl_sounds).play()       
        expl = Explosion(hit.rect.center,'lg')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        newmob()
    
    #火山石与玩家炮弹碰撞检测
    hits = pygame.sprite.groupcollide(lavas,bullets,True,True)    
    for hit in hits:
        score += 50-hit.radius
        random.choice(expl_sounds).play()      
        expl = Explosion(hit.rect.center,'lg')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        newlava()

    #玩家与敌机碰撞检测
    hits = pygame.sprite.spritecollide(player,mobs,True,pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius*2
        expl = Explosion(hit.rect.center,'sm')
        all_sprites.add(expl)
        newmob()
        if player.shield <= 0: 
            player_die_sound.play()
            death_explosion = Explosion(player.rect.center,'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100

    #玩家与火山石碰撞检测
    hits = pygame.sprite.spritecollide(player,lavas,True,pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius*2
        expl = Explosion(hit.rect.center,'sm')
        all_sprites.add(expl)
        newlava()
        if player.shield <= 0: 
            player_die_sound.play()
            death_explosion = Explosion(player.rect.center,'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100
    
    #玩家与敌机炮弹碰撞检测
    hits = pygame.sprite.spritecollide(player,enemies_bullets,True,pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius*2
        expl = Explosion(hit.rect.center,'sm')
        all_sprites.add(expl)        
        if player.shield <= 0: 
            player_die_sound.play()
            death_explosion = Explosion(player.rect.center,'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100
    
    #玩家与补给碰撞检测
    hits = pygame.sprite.spritecollide(player,powerups,True)
    for hit in hits:
        if hit.type == 'shield':
            player.shield += random.randrange(10,30)
            if player.shield >= 100:
                player.shield = 100
        if hit.type == 'gun':
            player.powerup()

    if player.lives == 0 and not death_explosion.alive():
        pygame.time.wait(1000)
        screen.fill(BLACK)
        draw_text(screen, "Game Over", 40, WIDTH/2, HEIGHT/3)
        pygame.display.update()
        pygame.time.wait(3000)
        menu_display = True

    #背景画卷向下滚动
    screen.fill(BLACK)    
    screen.blit(background,(0,height))
    height += 2
    if height >= -168:
        height = -936

    all_sprites.draw(screen)
    draw_text(screen,str(score),18,WIDTH/2,10)
    draw_shield_bar(screen,5,5,player.shield)    
    draw_lives(screen,WIDTH-100,5,player.lives,player_mini_img)

    pygame.display.flip()    

pygame.quit()