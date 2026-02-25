import pygame
import random
import sys

# 初始化pygame并设置中文字体（解决乱码核心）
pygame.init()
pygame.font.init()
try:
    # Windows系统优先用微软雅黑，其他系统自动适配
    font = pygame.font.SysFont(["Microsoft YaHei", "SimHei", "Arial"], 25)
except:
    font = pygame.font.Font(None, 25)

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# 屏幕尺寸
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("贪吃蛇")

# 游戏时钟和速度（降低初始速度）
clock = pygame.time.Clock()
snake_speed = 8  # 数值越小速度越慢

# 蛇的初始设置
snake_block = 10
snake_list = []
snake_length = 3  # 初始蛇身长度

# 食物位置生成
def generate_food():
    return (
        random.randrange(1, (WIDTH // snake_block)) * snake_block,
        random.randrange(1, (HEIGHT // snake_block)) * snake_block
    )

food_pos = generate_food()

# 方向控制
direction = 'RIGHT'
change_to = direction

# 游戏主循环
def game_loop():
    global direction, change_to, snake_list, snake_length, food_pos

    game_over = False
    game_close = False

    # 初始位置居中
    x1 = WIDTH / 2
    y1 = HEIGHT / 2

    x1_change = snake_block  # 初始向右移动
    y1_change = 0

    # 初始化蛇身（长度3）
    snake_list = []
    snake_length = 3
    for i in range(snake_length):
        snake_list.append([x1 - i*snake_block, y1])

    while not game_over:
        # ========== 修复核心：确保事件循环能捕获所有按键 ==========
        # 先处理全局事件（包括游戏结束界面的按键）
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                game_close = False
            # 游戏结束时的按键判定
            if game_close and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:  # Q退出
                    game_over = True
                    game_close = False
                if event.key == pygame.K_c:  # C重新开始
                    game_loop()
            # 游戏进行中的方向按键
            if not game_close and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and direction != 'RIGHT':
                    change_to = 'LEFT'
                if event.key == pygame.K_RIGHT and direction != 'LEFT':
                    change_to = 'RIGHT'
                if event.key == pygame.K_UP and direction != 'DOWN':
                    change_to = 'UP'
                if event.key == pygame.K_DOWN and direction != 'UP':
                    change_to = 'DOWN'

        # 游戏结束界面绘制
        if game_close:
            screen.fill(BLACK)
            text = font.render("游戏结束！按Q退出，按C重新开始", True, RED)
            screen.blit(text, [WIDTH / 8, HEIGHT / 3])
            pygame.display.update()
            clock.tick(10)  # 降低结束界面帧率，减少资源占用
            continue  # 跳过后续游戏逻辑

        # 更新移动方向（修复原代码的方向错误）
        if change_to == 'LEFT':
            x1_change = -snake_block
            y1_change = 0
        elif change_to == 'RIGHT':
            x1_change = snake_block
            y1_change = 0
        elif change_to == 'UP':
            y1_change = -snake_block
            x1_change = 0
        elif change_to == 'DOWN':  # 原代码错写成RIGHT，导致向下按键无效
            y1_change = snake_block
            x1_change = 0

        direction = change_to

        # 更新蛇头位置
        x1 += x1_change
        y1 += y1_change

        # 撞墙判定
        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            game_close = True

        # 绘制背景和食物
        screen.fill(BLACK)
        pygame.draw.rect(screen, RED, [food_pos[0], food_pos[1], snake_block, snake_block])

        # 更新蛇身
        snake_head = [x1, y1]
        snake_list.append(snake_head)

        # 保持蛇身长度
        if len(snake_list) > snake_length:
            del snake_list[0]

        # 撞自己判定
        for segment in snake_list[:-1]:
            if segment == snake_head:
                game_close = True

        # 绘制蛇身
        for segment in snake_list:
            pygame.draw.rect(screen, GREEN, [segment[0], segment[1], snake_block, snake_block])

        # 更新屏幕
        pygame.display.update()

        # 吃到食物判定
        if x1 == food_pos[0] and y1 == food_pos[1]:
            food_pos = generate_food()
            snake_length += 1

        # 控制帧率
        clock.tick(snake_speed)

    # 退出游戏
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    # 自动安装pygame（清华源）
    import subprocess
    try:
        import pygame
    except ImportError:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "pygame",
            "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
        ])
        import pygame
    game_loop()