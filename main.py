import pygame
import sys
import random
import os

class SpriteBase:                               # 实体基类
    def __init__(self, x, y, image, speed, screen):     # 实体本身、坐标、图像、速度
        self.x = x
        self.y = y
        self.image = image
        self.speed = speed
        self.screen = screen
        self.width = image.get_width()
        self.height = image.get_height()

    def move(self):
        pass

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def get_rect(self):                      # 碰撞矩形
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return rect.inflate(-self.width * 0.2, -self.height * 0.4)

    @property
    def screen_width(self):
        return self.screen.get_width()

    @property
    def screen_height(self):
        return self.screen.get_height()


class Player(SpriteBase):                   # 玩家子类
    def __init__(self, screen):
        self.screen = screen
        x = self.screen_width//2
        y = self.screen_height // 3 * 2
        speed = self.screen_width // 100
        image = pygame.image.load("Player.png")             # 加载玩家飞机
        image = pygame.transform.scale(image, (80, 80))     # 缩放到80*80


        super().__init__(x, y, image, speed, screen)

    def move(self, keys):                   # 操作
        if keys[pygame.K_LEFT]:             # 左
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:            # 右
            self.x += self.speed
        if self.x < 0:                      # 左边界循环
            self.x = self.screen.get_width() - self.width
        if self.x + self.width > self.screen.get_width():       # 右边界循环
            self.x = 0              

class Enemy(SpriteBase):                    # 敌人子类
    def __init__(self, x, y, speed, screen):
        image = pygame.image.load("Enemy.png")              # 加载敌人飞机
        image = pygame.transform.scale(image, (50, 50))     # 缩放
        image = pygame.transform.rotate(image, 180)         # 旋转180度，机头朝下
        super().__init__(x, y, image, speed, screen)

    def move(self):
        self.y += self.speed                # 暂时只向下移动


class Bullet(SpriteBase):                   # 攻击：子弹
    def __init__(self, x, y,  speed, screen):
        image = pygame.image.load("Bullet.png")                 # 加载子弹
        image = pygame.transform.scale(image, (20, 20))         # 缩放

        super().__init__(x, y, image, speed, screen)

    def move(self):
        self.y -= self.speed

class Renderer:
    def __init__(self,screen):
        self.screen = screen

    # 更新每个实体在屏幕上的位置
    def draw_all(self, *sprites):
        for item in sprites:
            if isinstance(item, (list, tuple)):
                for sprite in item:
                    sprite.draw(self.screen)
            else:
                item.draw(self.screen)

class Game:
    def __init__(self):
        # 窗口宽度
        self.window_width = 1600
        # 窗口长度
        self.window_height = 900

        pygame.init()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("飞机大战 O(∩_∩)O 这么长的标题栏我想多写一点东西于是就这样了")
        self.clock = pygame.time.Clock()

        self.game_over = False              # 创建对局状态

        self.player = Player(self.screen)   # 创建玩家实体

        self.enemies = []                   # 创建敌人群
           
        self.bullets = []                   # 创建子弹列表

        self.spawn_timer = 0                # 生成帧计数器
        self.spawn_interval = 60            # 60帧生成一架敌机

        self.score = 0                      # 创建分数计数器

        self.renderer = Renderer(self.screen)   # 创建渲染器

        # 字体加载
        local_ttf = "字小魂方块黑(商用需授权).ttf"
        try:
            if os.path.exists(local_ttf):
                self.font = pygame.font.Font(local_ttf, 30)
            else:
                raise FileNotFoundError("未找到指定字体 \"字小魂方块黑(商用需授权)\"")
        except Exception as e:
            self.font = pygame.font.match_font("字小魂方块黑(商用需授权),microsoftyahei,msyh,simhei,dengxian,simsun", 30)        

    # 判断a\b两实例是否碰撞
    @staticmethod
    def rect_check(a:SpriteBase, b:SpriteBase):         
        if a.get_rect().colliderect(b.get_rect()):
            return True
        else:
            return False

    # 生成敌机                                  
    def spawn_enemy(self):                              
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            x = random.randint(0, self.window_width - 40)               # 随机位置
            self.enemies.append(Enemy(x, -20, 3, self.screen))          # 窗口外出现

    # 对局逻辑
    def main_while(self):
        while not self.game_over:
            for event in pygame.event.get():
        
                # 显示当前事件是什么
                # print(event)
        
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # 发射子弹
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    position = self.player.x + (self.player.width//2) - 3
                    self.bullets.append(Bullet(position, self.player.y, 8, self.screen))
                    
        
            self.screen.fill((0, 0, 0))
            operation = pygame.key.get_pressed()                            # 读取操作
            self.player.move(operation)                                     # 执行移动操作


        
            # 生成敌机
            self.spawn_enemy()
        
            # 敌人移动逻辑
            for enemy in self.enemies:
                enemy.move()
        
            # 子弹移动逻辑
            for bullet in self.bullets:
                bullet.move()
        
            # 碰撞逻辑：不写在子弹移动逻辑中的原因是，避免在操作中修改列表
            for bullet in self.bullets[:]:
                for enemy in self.enemies:
                    if self.rect_check(bullet, enemy):
                        self.bullets.remove(bullet)
                        self.enemies.remove(enemy)
                        self.score += 10
                        print("得分：", self.score)
                        break
        
            for enemy in self.enemies:
                if self.rect_check(self.player, enemy):
        
                    # 对局结束
                    print("对局结束")
        
                    self.game_over = True
                    break

            for bullet in self.bullets[:]:
                if bullet.y + bullet.height < 0:                # 子弹飞出顶部
                    self.bullets.remove(bullet)
            for enemy in self.enemies[:]:
                if enemy.y > self.window_height:                # 敌人飞出底部
                    self.enemies.remove(enemy)            

            self.renderer.draw_all(self.enemies, self.player, self.bullets)
            
            # 分数显示
            text = self.font.render(f"分数：{self.score}", True, (255, 255, 255))
            self.screen.blit(text, (10, 10))
            pygame.display.flip()                   
            self.clock.tick(60)

    # 游戏控制逻辑
    def run(self):


        # 进入游戏机
        self.main_while()

        # 结束环节
        text = self.font.render(f"游戏结束  得分：{self.score}", True, (255, 255, 255))
        text = pygame.transform.scale(text, (self.screen.width//5 * 2, self.screen.height//10))
        self.screen.blit(text, (self.screen.width//2 - self.screen.width//5, self.screen.height//2 - self.screen.height//20))
        pygame.display.flip()       
        pygame.time.wait(2000)

        # 退出窗口
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Game().run()   # 实例化并调用
