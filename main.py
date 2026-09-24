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
        return pygame.Rect(self.x, self.y, self.width, self.height)

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
        image = pygame.Surface((50, 50))    # 临时纯色方块当飞机
        image.fill((0, 255, 0))             # 绿色


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
        image = pygame.Surface((40, 40))    # 临时
        image.fill((255, 0, 0))             # 红色
        super().__init__(x, y, image, speed, screen)

    def move(self):
        self.y += self.speed                # 暂时只向下移动


class Bullet(SpriteBase):                   # 攻击：子弹
    def __init__(self, x, y,  speed, screen):
        image = pygame.Surface((10, 10))
        image.fill((0, 0, 255))             # 蓝色
        super().__init__(x, y, image, speed, screen)

    def move(self):
        self.y -= self.speed

class Game:
    def __init__(self):
        # 窗口宽度
        self.window_width = 600
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

    # 更新每个实体在屏幕上的位置
    @staticmethod
    def all_sprite(screen, *sprites):
        for item in sprites:
            if isinstance(item, (list, tuple)):
                for sprite in item:
                    sprite.draw(screen)
            else:
                item.draw(screen)

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
            # self.player.draw(self.screen)                                 # 把移动后的玩家更新到屏幕上
            self.all_sprite(self.screen, self.enemies, self.player, self.bullets)          # 更新全部实体到屏幕
        
            # 生成敌机
            self.spawn_enemy()
        
            # 敌人移动逻辑
            for enemy in self.enemies:
                enemy.move()
                # enemy.draw(self.screen)         
        
            # 子弹移动逻辑
            for bullet in self.bullets:
                bullet.move()
                # bullet.draw(self.screen)
        
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
        self.screen.blit(text, (90, 280))
        pygame.display.flip()       
        pygame.time.wait(2000)

        # 退出窗口
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Game().run()   # 实例化并调用