from collections import deque

import pygame
import sys
import random
import time
import math

# 게임 초기화
pygame.init()

# 화면 크기 설정
WIDTH, HEIGHT = 600, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("요리조리 미로")

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
CYAN = (0, 200, 255)

# 블록 크기
BLOCK_SIZE = 40

# 이미지 경로들
image_paths = {
    'way': ["way1.png", "way2.png", "way3.png", "way4.png", "way5.png"],
    'wall': ["wall1.png", "wall2.png", "wall3.png", "wall4.png", "wall5.png"],
    'obstacles': ["gold_obstacle.png", "ice_obstacle.png", "lava.png", "umbrella.png"],
    'player': "player.png",
    'elements': ["tomato.png", "shrimp.png", "pepper.png", "cream.png", "basil.png", "question_mark.png"]
}


# 이미지 로딩 및 크기 조정 함수
def load_images(paths, size=(BLOCK_SIZE, BLOCK_SIZE)):
    images = {}
    for key, path_list in paths.items():
        if isinstance(path_list, list):
            images[key] = [pygame.transform.scale(pygame.image.load(p), size) for p in path_list]
        else:
            images[key] = pygame.transform.scale(pygame.image.load(path_list), size)
    return images

# 이미지 로드
images = load_images(image_paths)

# 폰트 설정 (한글 지원 폰트 사용)
FONT = pygame.font.Font(r"C:\Users\sso06\OneDrive\Documents\DungGeunMo.ttf", 36)

# 바람 방향 정의
DIRECTIONS = ["UP", "DOWN", "LEFT", "RIGHT"]
wind_direction = random.choice(DIRECTIONS)
last_wind_change_time = time.time()

#배경음악
pygame.mixer.music.load("background_music.mp3")  # 경로에 맞게 수정
pygame.mixer.music.set_volume(0.5)  # 배경 음악 볼륨 설정 (0.0에서 1.0 사이)
pygame.mixer.music.play(-1, 0.0)  # 무한 반복 재생, 처음부터 시작

collected_items = []
reward_message = None
reward_message_start_time = None
blink_count = 0  # 현재 깜빡임 횟수
max_blinks = 3  # 최대 깜빡임 횟수
blink_interval = 0.35  # 깜빡임 간격 (초)

level_rewards = {
    1: {"message": "토마토를 획득했다!", "image": images['elements'][0]},
    2: {"message": "새우를 획득했다!", "image": images['elements'][1]},
    3: {"message": "고추를 획득했다!", "image": images['elements'][2]},
    4: {"message": "크림을 획득했다!", "image": images['elements'][3]},
    5: {"message": "바질을 획득했다!", "image": images['elements'][4]},
}

collected_items = [images['elements'][5]] * 5  # 총 5개의 물음표로 시작

# 보상 메시지를 그리는 함수
def draw_reward_message(message, blink_start_time):
    """보상 메시지를 화면에 깜빡거리며 표시"""
    global blink_count

    elapsed_time = time.time() - blink_start_time
    blink_on = int(elapsed_time / blink_interval) % 2 == 0

    if blink_count < max_blinks * 3:
        if blink_on:
            text = FONT.render(message, True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN.get_width() // 2, SCREEN.get_height() - 50))  # 화면 하단 중앙
            SCREEN.blit(text, text_rect)
    else:
        return False

    # 깜빡임 횟수 업데이트
    if int(elapsed_time / blink_interval) > blink_count:
        blink_count += 1

    return True

#획득 재료 업데이트
def update_collected_items(level):
    if level in level_rewards:
        item_image = level_rewards[level]["image"]
        collected_items[level - 1] = item_image

def show_intro_screen():
    intro_running = True

    # 각 텍스트 크기 조정
    title_font = pygame.font.Font(r"C:\Users\sso06\OneDrive\Documents\DungGeunMo.ttf", 50)
    story_font = pygame.font.Font(r"C:\Users\sso06\OneDrive\Documents\DungGeunMo.ttf", 25)
    start_font = pygame.font.Font(r"C:\Users\sso06\OneDrive\Documents\DungGeunMo.ttf", 40)

    jump_height = 5
    start_y = 300

    while intro_running:
        SCREEN.fill(WHITE)

        title_text = title_font.render("요리 조리 미로", True, BLACK)
        story_text1 = story_font.render("미로를 통과하며 다양한 재료들을 획득하자!", True, BLACK)
        story_text2 = story_font.render("용기를 내어 목적지까지 도달하세요!", True, BLACK)

        # 텍스트 출력
        SCREEN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
        SCREEN.blit(story_text1, (WIDTH // 2 - story_text1.get_width() // 2, 150))
        SCREEN.blit(story_text2, (WIDTH // 2 - story_text2.get_width() // 2, 200))

        # 폴짝 뛰는 효과 구현
        current_time = pygame.time.get_ticks()
        jump_offset = jump_height * math.sin(current_time / 500.0 * 2 * math.pi)

        # 주인공 이미지 표시 (y값에 jump_offset을 더해주어 폴짝 뛰게 만듬)
        player_intro_image = pygame.transform.scale(images['player'], (120, 120))
        SCREEN.blit(player_intro_image, (WIDTH // 2 - 60, start_y + jump_offset))

        # "게임 시작" 안내
        start_text = start_font.render("Press SPACE to Start", True, RED)
        SCREEN.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 500))

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    intro_running = False

        pygame.display.flip()
        pygame.time.Clock().tick(60)

# 랜덤 미로 생성 함수
def generate_maze(width, height):
    maze = [[1] * width for _ in range(height)]  # 벽으로 채운 초기 미로 생성
    start_x, start_y = 1, 1
    maze[start_y][start_x] = 2  # 시작점 (2는 시작점으로 표시)

    def dfs(x, y):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)  # 이동 방향을 무작위로 섞기

        for dx, dy in directions:
            nx, ny = x + dx * 2, y + dy * 2  # 2칸씩 이동
            if 0 < nx < width - 1 and 0 < ny < height - 1 and maze[ny][nx] == 1:
                maze[ny][nx] = 0
                maze[y + dy][x + dx] = 0
                dfs(nx, ny)

    # DFS로 미로 생성
    dfs(start_x, start_y)

    # 목적지 설정: 미로의 가장 먼 점 찾기
    def farthest_point(start_x, start_y):
        from collections import deque
        visited = [[False] * width for _ in range(height)]
        queue = deque([(start_x, start_y, 0)])
        visited[start_y][start_x] = True
        farthest = (start_x, start_y, 0)

        while queue:
            x, y, dist = queue.popleft()
            if dist > farthest[2]:
                farthest = (x, y, dist)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 < nx < width and 0 < ny < height and not visited[ny][nx] and maze[ny][nx] == 0:
                    visited[ny][nx] = True
                    queue.append((nx, ny, dist + 1))
        return farthest

    end_x, end_y, _ = farthest_point(start_x, start_y)
    maze[end_y][end_x] = 3  # 목적지 (3으로 표시)

    return maze

def draw_maze(maze):
    maze_offset_y = 200

    # 기본 이미지 설정
    wall_image = None
    grass_image = None
    destination_images = {}  # 목적지별 이미지를 저장할 딕셔너리
    start_image = pygame.image.load('start.png')

    # 현재 게임 단계에 맞게 벽 이미지 설정
    if current_level == 0:
        wall_image = images['wall'][0]  # wall_image1
        grass_image = images['way'][0]  # way_image1
        destination_images = {3: images['elements'][0]}  # tomato
    elif current_level == 1:
        wall_image = images['wall'][1]  # wall_image2
        grass_image = images['way'][1]  # way_image2
        destination_images = {3: images['elements'][2]}  # pepper
    elif current_level == 2:
        wall_image = images['wall'][2]  # wall_image3
        wall_image = images['wall'][2]  # wall_image3
        destination_images = {3: images['elements'][2]}  # pepper
    elif current_level == 3:
        wall_image = images['wall'][3]  # wall_image4
        grass_image = images['way'][3]  # way_image4
        destination_images = {3: images['elements'][3]}  # cream
    elif current_level == 4:
        wall_image = images['wall'][4]  # wall_image5
        grass_image = images['way'][4]  # way_image5
        destination_images = {3: images['elements'][4]}  # basil

    # 오류를 방지 위해 디폴트 이미지 설정
    if wall_image is None:
        wall_image = pygame.transform.scale(images['wall'][4], (BLOCK_SIZE, BLOCK_SIZE))

    if grass_image is None:
        grass_image = pygame.transform.scale(images['way'][4], (BLOCK_SIZE, BLOCK_SIZE))

    for y in range(len(maze)):
        for x in range(len(maze[y])):
            if maze[y][x] == 1:  # 벽
                SCREEN.blit(wall_image, (x * BLOCK_SIZE, y * BLOCK_SIZE + maze_offset_y, BLOCK_SIZE, BLOCK_SIZE))
            elif maze[y][x] == 0:  # 길
                SCREEN.blit(grass_image, (x * BLOCK_SIZE, y * BLOCK_SIZE + maze_offset_y, BLOCK_SIZE, BLOCK_SIZE))
            elif maze[y][x] == 2:  # 시작점
                SCREEN.blit(grass_image, (x * BLOCK_SIZE, y * BLOCK_SIZE + maze_offset_y, BLOCK_SIZE, BLOCK_SIZE))

                start_image_resized = pygame.transform.scale(start_image, (BLOCK_SIZE, BLOCK_SIZE))
                SCREEN.blit(start_image_resized, (x * BLOCK_SIZE, y * BLOCK_SIZE + maze_offset_y))
            elif maze[y][x] == 3:  # 목적지
                SCREEN.blit(grass_image, (x * BLOCK_SIZE, y * BLOCK_SIZE + maze_offset_y, BLOCK_SIZE, BLOCK_SIZE))

                # 목적지 이미지가 설정되어 있으면 해당 이미지를 사용
                if 3 in destination_images:
                    destination_image = destination_images[3]
                    destination_image = pygame.transform.scale(destination_image, (BLOCK_SIZE, BLOCK_SIZE))
                    SCREEN.blit(destination_image, (x * BLOCK_SIZE, y * BLOCK_SIZE + maze_offset_y))  # 목적지 이미지 출력
                else:
                    pygame.draw.rect(SCREEN, RED, (x * BLOCK_SIZE, y * BLOCK_SIZE + maze_offset_y, BLOCK_SIZE, BLOCK_SIZE))

# 2단계의 황금색 장애물 좌표 초기화
gold_obstacles = []

# 하늘색 오브젝트 관련 변수
cyan_objects = []
cyan_last_collected = {}  # 하늘색 오브젝트의 마지막 경유 시간

# 현재 단계와 플레이어 위치 초기화
current_level = 0
player_x, player_y = 1, 1

# 빙판길 관련 변수 초기화
ice_paths = []
ice_cross_count = 0

# 최근 밟은 빙판길 위치를 추적하기 위한 변수
last_ice_position = None

# 빨간 오브젝트(용암) 관련 변수
lava_objects = []
lava_last_spawn_time = 0
lava_spawn_interval = 3  # 용암 생성 간격 (초)
lava_duration = 2  # 용암 지속 시간 (초)

# 연기 관련 변수
smoke_position_x = 0  # 연기의 초기 x 위치
smoke_speed = 3       # 연기의 이동 속도
smoke_width = 100     # 연기의 폭
smoke_height = HEIGHT  # 연기의 높이 (화면 전체 높이)
smoke_color = (100, 100, 100, 128)  # 연기의 색상 (회색, 반투명)

#모든 아이템 출력
def draw_collected_items():
    item_start_x = 20
    item_start_y = 150
    item_spacing = 60

    for i, item in enumerate(collected_items):
        SCREEN.blit(item, (item_start_x + i * item_spacing, item_start_y))

# 바람 방향 업데이트 함수
def change_wind_direction():
    global wind_direction, last_wind_change_time
    if time.time() - last_wind_change_time > 5:
        wind_direction = random.choice(DIRECTIONS)
        last_wind_change_time = time.time()

# 바람 방향 표시
def draw_wind_arrow():
    # 현재 단계가 3단계 (인덱스 2)일 때만 표시
    if current_level == 2:
        arrow_text = ""
        if wind_direction == "UP":
            arrow_text = "↑"
        elif wind_direction == "DOWN":
            arrow_text = "↓"
        elif wind_direction == "LEFT":
            arrow_text = "←"
        elif wind_direction == "RIGHT":
            arrow_text = "→"

        arrow_surface = FONT.render(f"바람 방향: {arrow_text}", True, WHITE)
        arrow_rect = arrow_surface.get_rect(center=(WIDTH // 2, 90))
        SCREEN.blit(arrow_surface, arrow_rect)

# 이동 방향이 바람과 반대인지 확인
def is_opposite_direction(player_move, wind_direction):
    return (player_move == "UP" and wind_direction == "DOWN") or \
        (player_move == "DOWN" and wind_direction == "UP") or \
        (player_move == "LEFT" and wind_direction == "RIGHT") or \
        (player_move == "RIGHT" and wind_direction == "LEFT")

# 플레이어 생명 초기화
lives = 3
message = ""
message_start_time = None
game_over = False
moving = False

# 경로 기록
path = []
draw_path = []

# 황금색 장애물 배치 함수
def place_gold_obstacles(maze):
    global gold_obstacles
    gold_obstacles = []
    while len(gold_obstacles) < 4:
        x, y = random.randint(0, len(maze[0]) - 1), random.randint(0, len(maze) - 1)
        if maze[y][x] == 0 and (x, y) not in gold_obstacles:
            gold_obstacles.append((x, y))

# 하늘색 오브젝트 배치 함수
def place_cyan_objects(maze):
    global cyan_objects, cyan_last_collected
    cyan_objects = []
    cyan_last_collected = {}
    while len(cyan_objects) < 3:
        x, y = random.randint(0, len(maze[0]) - 1), random.randint(0, len(maze) - 1)
        if maze[y][x] == 0 and (x, y) not in cyan_objects:
            cyan_objects.append((x, y))
            cyan_last_collected[(x, y)] = 0  # 초기화 시간 설정

# 빙판길 배치 함수 (4단계 전용)
def place_ice_paths(maze, start, end):
    global ice_paths
    ice_paths = []
    while len(ice_paths) < 7:
        x, y = random.randint(0, len(maze[0]) - 1), random.randint(0, len(maze) - 1)
        # 플레이어가 이동 가능한 경로(0)인 경우에만 빙판길 배치
        if maze[y][x] == 0 and (x, y) not in ice_paths:
            ice_paths.append((x, y))

# 빙판길 패널티 체크 함수
def check_ice_penalty():
    global ice_cross_count, player_x, player_y, message, message_start_time, path, draw_path, moving, last_ice_position
    # 5단계에서는 패널티를 적용하지 않음
    if current_level == 4:  # 5단계 인덱스는 4
        return

    if (player_x, player_y) in ice_paths:
        # 최근 밟은 빙판길 위치와 현재 위치가 다를 때만 카운트 증가
        if last_ice_position != (player_x, player_y):
            ice_cross_count += 1
            last_ice_position = (player_x, player_y)  # 현재 위치를 기록
            if ice_cross_count >= 3:
                # 4단계 시작 위치로 즉시 리스폰
                player_x, player_y = 1, 1  # 4단계 시작 위치
                ice_cross_count = 0  # 빙판길 경유 횟수 초기화
                last_ice_position = None  # 최근 밟은 위치 초기화
                path = []  # 경로 초기화
                draw_path = []  # 경로 그리기 초기화
                moving = False  # 이동 중지
                message = "빙판길을 3번 밟았습니다! 시작 지점으로 즉시 리스폰됩니다."
                message_start_time = time.time()
                return  # 즉시 함수 종료하여 이동 중단
        # 빙판길 위에서는 자동 이동
        else:
            # 다음 칸으로 자동 이동
            if path:
                next_x, next_y = path[0]
                # 빙판길 위에서 경로 따라 이동
                if maze[next_y][next_x] == 0:
                    player_x, player_y = next_x, next_y
                    path.pop(0)
            else:
                moving = False
    else:
        # 빙판길이 아닌 위치로 이동했을 때 최근 위치 초기화
        last_ice_position = None

# 빨간 오브젝트(용암) 생성 함수
def spawn_lava(maze):
    global lava_objects
    lava_objects = []
    num_lava = random.randint(3, 6)  # 랜덤한 개수의 용암 생성
    while len(lava_objects) < num_lava:
        x, y = random.randint(0, len(maze[0]) - 1), random.randint(0, len(maze) - 1)
        if maze[y][x] == 0 and (x, y) not in lava_objects:  # 이동 가능한 경로에만 생성
            lava_objects.append((x, y))

def draw_smoke():
    global smoke_position_x
    # 연기 이동
    smoke_position_x += smoke_speed
    if smoke_position_x > WIDTH:  # 화면을 넘어가면 다시 왼쪽으로
        smoke_position_x = -smoke_width

    # 연기 그리기 (구름 모양, 불투명)
    smoke_surface = pygame.Surface((smoke_width, 400), pygame.SRCALPHA)  # 높이를 400으로 설정
    smoke_surface.fill((0, 0, 0, 0))  # 완전 투명으로 초기화

    # 원형 패턴을 반복해서 그려 구름처럼 보이게 설정
    for i in range(7):  # 더 많은 원을 사용하여 크기를 확장
        pygame.draw.circle(
            smoke_surface,
            (100, 100, 100, 255),  # 연기 색상 (회색, 완전 불투명)
            (50, 20 + i * 60),  # 원의 중심 (x는 고정, y는 위아래로 퍼지게 설정)
            50  # 원의 반지름을 키움
        )

    # 연기를 화면 상단 300 픽셀 아래에 표시
    SCREEN.blit(smoke_surface, (smoke_position_x, 200))

# 시간 관련 변수
time_limit = 60
start_time = time.time()

# 게임 초기화 단계에서 미로 생성
maze = generate_maze(15, 9)

# 단계 초기화 함수 수정
def reset_level():
    global player_x, player_y, start_time, maze  # 전역 변수 maze 사용
    player_x, player_y = 1, 1
    start_time = time.time()
    # 새로운 단계에 진입할 때만 미로를 생성
    maze = generate_maze(15, 9)  # 새로운 미로 생성

# 게임 초기화 단계에서 미로 생성
maze = generate_maze(15, 9)

# 메시지 표시 함수
def draw_message(text, y_offset):
    # 메시지 크기 조절
    if text in ("바람과 반대 방향으로 이동할 수 없습니다!", "황금 장애물에 닿았습니다! 1단계부터 다시 시작합니다."):
        font = pygame.font.Font(r"C:\Users\sso06\OneDrive\Documents\DungGeunMo.ttf", 25)  # 글씨 크기 25
    else:
        font = pygame.font.Font(r"C:\Users\sso06\OneDrive\Documents\DungGeunMo.ttf", 30)  # 기본 글씨 크기

    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, y_offset))
    SCREEN.blit(text_surface, text_rect)

# 남은 시간 표시 함수
def draw_timer():
    global start_time
    elapsed_time = time.time() - start_time
    remaining_time = max(0, int(time_limit - elapsed_time))
    timer_text = FONT.render(f"남은 시간: {remaining_time}초", True, WHITE)
    SCREEN.blit(timer_text, (WIDTH - 280, 30))
    return remaining_time

# 메인 실행
if __name__ == "__main__":
    show_intro_screen()  # 인트로 화면 표시

# 게임 루프
while True:

    # 5단계에서 용암 생성 및 관리
    if current_level == 4:  # 5단계 인덱스는 4
        # 용암 생성 간격에 따라 새로 생성
        if time.time() - lava_last_spawn_time > lava_spawn_interval:
            spawn_lava(maze)
            lava_last_spawn_time = time.time()

        # 용암이 생성된 지 lava_duration 초가 지나면 제거
        if time.time() - lava_last_spawn_time > lava_duration:
            lava_objects = []  # 용암 제거

        # 플레이어가 용암에 닿았는지 확인
        if (player_x, player_y) in lava_objects:
            game_over = True
            message = "용암에 닿았습니다! 게임 오버!"

    # 4단계에 진입하면 한 번만 빙판길 배치
    if current_level == 3 and not ice_paths:  # 4단계에서만 적용
        start = (1, 1)  # 시작 위치
        end = (len(maze[0]) - 2, len(maze) - 2)  # 종료 위치
        place_ice_paths(maze, start, end)

    # 플레이어 이동 중 빙판길 체크
    if current_level == 3:  # 4단계에서만 빙판길 체크
        check_ice_penalty()

    change_wind_direction()

    # 3단계에 진입하면 한 번만 하늘색 오브젝트 배치
    if current_level == 2 and not cyan_objects:
        place_cyan_objects(maze)

    # 다른 단계에서는 하늘색 오브젝트 유지
    if current_level != 2:
        cyan_objects = []  # 3단계가 아니면 하늘색 오브젝트 제거

    # 2단계에서 황금색 장애물 배치
    if current_level == 1 and not gold_obstacles:
        place_gold_obstacles(maze)
    elif current_level != 1:
        gold_obstacles = []  # 다른 단계에서는 황금색 장애물 제거

    # 3단계일 때만 바람 화살표 그리기
    if current_level == 2:
        draw_wind_arrow()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # 마우스 클릭 시 경로 초기화 및 그리기 시작
        if not game_over and event.type == pygame.MOUSEBUTTONDOWN:
            draw_path = [(player_x * BLOCK_SIZE + BLOCK_SIZE // 2, player_y * BLOCK_SIZE + 200 + BLOCK_SIZE // 2)]
            moving = False

        # 마우스 버튼을 떼면 이동 시작
        elif not game_over and event.type == pygame.MOUSEBUTTONUP:
            path = [(pos[0] // BLOCK_SIZE, (pos[1] - 200) // BLOCK_SIZE) for pos in draw_path]
            draw_path = []
            moving = True

    # 이동 처리 중 빙판길 자동 이동 추가
    if moving and path:
        next_x, next_y = path.pop(0)  # 경로에서 다음 위치 가져오기

        # 이동 가능한 경우 업데이트
        if maze[next_y][next_x] == 0:
            player_x, player_y = next_x, next_y

            # 빙판길 위에 있는 경우 추가 이동 처리
            if (player_x, player_y) in ice_paths:
                check_ice_penalty()  # 빙판길 위에서 다시 확인

    # 마우스 클릭하고 드래그하는 동안 경로 기록
    if not game_over and pygame.mouse.get_pressed()[0] and not moving:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if draw_path and (mouse_x, mouse_y) != draw_path[-1]:
            draw_path.append((mouse_x, mouse_y))

    # 이동 모드일 때, 경로 따라 한 칸씩 이동
    if moving and path:
        next_x, next_y = path.pop(0)  # 경로에서 다음 위치 가져오기

        if current_level == 1 and (next_x, next_y) in gold_obstacles:
            current_level = 0
            lives = 3
            gold_obstacles = []
            message = "해파리에 닿았습니다! 1단계 리턴!"
            player_x, player_y = 1, 1
            message_start_time = time.time()
            moving = False
            path = []
            start_time = time.time()  # 제한 시간 초기화
            maze = generate_maze(15, 9)  # 새로운 미로 생성 (1단계 리셋)

        # 이동 방향 결정
        if next_x > player_x:
            player_move = "RIGHT"
        elif next_x < player_x:
            player_move = "LEFT"
        elif next_y > player_y:
            player_move = "DOWN"
        elif next_y < player_y:
            player_move = "UP"
        else:
            player_move = None

        # 3단계에서 바람 패널티 적용 (이동하기 전에 체크)
        if current_level == 2 and is_opposite_direction(player_move, wind_direction):
            moving = False
            path = []
            message = "바람과 반대 방향으로 이동할 수 없습니다!"
            message_start_time = time.time()
            continue  # 이동 중단

        # 4단계에 빙판길 배치
        if current_level == 3 and not ice_paths:
            place_ice_paths(maze)

        # 플레이어 이동 중 빙판길 체크
        if current_level == 3:
            check_ice_penalty()

        # 벽에 닿으면 이동 중지
        elif maze[next_y][next_x] == 1:
            lives -= 1
            message = f"벽에 부딪혔습니다! 남은 생명: {lives}"
            message_start_time = time.time()
            moving = False  # 이동 모드 비활성화
            path = []  # 이동 중단

            # 생명이 0이면 게임 오버
            if lives <= 0:
                game_over = True
                message = "게임 오버! 모든 생명을 잃었습니다."
        else:
            player_x, player_y = next_x, next_y  # 벽이 아닐 때만 이동

        if (player_x, player_y) in cyan_objects:
            current_time = time.time()
            if current_time - cyan_last_collected[(player_x, player_y)] >= 10:
                start_time += 5
                message = "우산 오브젝트 경유! 5초 추가!"
                message_start_time = current_time
                cyan_last_collected[(player_x, player_y)] = current_time

            # 이동 가능한 경우 업데이트
        if maze[next_y][next_x] != 1 and not is_opposite_direction(player_move, wind_direction):
            player_x, player_y = next_x, next_y

            # 도착점에 도착하면 다음 단계로 이동
            if maze[player_y][player_x] == 3:
                current_level += 1
                if current_level >= 5:
                    game_over = True
                    message = "축하합니다! 모든 단계를 클리어했습니다!"
                    current_level = len(maze) - 1  # 인덱스 오류 방지
                    collected_items[4] = images['elements'][4]

                else:
                    reward_message = None

                    if current_level in level_rewards:
                        reward_data = level_rewards[current_level]
                        reward_message = reward_data["message"]
                        item_image = reward_data["image"]

                        collected_items[current_level - 1] = item_image
                        reward_message_start_time = time.time()
                        blink_count = 0

                        message = f"다음 단계로 이동합니다: {current_level + 1} 단계"

                        player_x, player_y = 1, 1
                        path = []
                        moving = False
                        message_start_time = time.time()
                        reset_level()

                        if current_level == 1:
                            place_gold_obstacles(maze)

    # 메시지 사라짐 처리 (3초 뒤에 사라지게 설정)
    if message_start_time and time.time() - message_start_time > 3:
        message = ""
        message_start_time = None

    # 남은 시간 확인
    remaining_time = draw_timer()
    if remaining_time == 0 and not game_over:
        game_over = True
        message = "시간 초과! 게임 오버입니다."

    # 화면 그리기
    SCREEN.fill(BLACK)
    draw_collected_items()
    draw_maze(maze)

    #획득 재료 알림 깜빡이기
    if reward_message and reward_message_start_time:
        if not draw_reward_message(reward_message, reward_message_start_time):
            reward_message = None
            reward_message_start_time = None

    # 게임 루프 내 연기 이동 및 표시
    if current_level == 4:  # 5단계에서만 연기 표시
        draw_smoke()

    # 생명 표시
    lives_text = FONT.render(f"생명: {lives}", True, WHITE)
    SCREEN.blit(lives_text, (10, 30))

    # 남은 시간 표시
    draw_timer()

    # 메시지 표시
    if message and not game_over:
        draw_message(message, 120)

    # 용암(빨간 오브젝트) 그리기
    if current_level == 4:  # 5단계 인덱스는 4
        for (lx, ly) in lava_objects:
            SCREEN.blit(images['obstacles'][2], (lx * BLOCK_SIZE, ly * BLOCK_SIZE + 200))

    # 게임 루프 내 연기 이동 및 표시
    if current_level == 4:  # 5단계에서만 연기 표시
        draw_smoke()

    # 빙판길 그리기 (4단계 전용)
    if current_level == 3:
        for (ix, iy) in ice_paths:
            SCREEN.blit(images['obstacles'][1], (ix * BLOCK_SIZE, iy * BLOCK_SIZE + 200))

    # 하늘색 오브젝트 그리기
    if current_level == 2:
        for (cx, cy) in cyan_objects:
            SCREEN.blit(images['obstacles'][3], (cx * BLOCK_SIZE, cy * BLOCK_SIZE + 200))

    # 황금색 장애물 그리기
    if current_level == 1:
        for (gx, gy) in gold_obstacles:
            SCREEN.blit(images['obstacles'][0], (gx * BLOCK_SIZE, gy * BLOCK_SIZE + 200))

    # 경로 그리기
    if len(draw_path) > 1:
        pygame.draw.lines(SCREEN, GREEN, False, draw_path, 3)

    # 플레이어 그리기
    if not game_over:
        SCREEN.blit(images['player'], (player_x * BLOCK_SIZE, player_y * BLOCK_SIZE + 200))

    # 게임 오버 메시지
    if game_over:
        draw_message(message, HEIGHT // 2 + 240)
        draw_message("ESC를 눌러 종료하세요.", HEIGHT // 2 + 290)

    # 바람 화살표 그리기
    draw_wind_arrow()

    # 화면 업데이트
    pygame.display.flip()
    pygame.time.Clock().tick(30)

    # ESC 키로 게임 종료
    if game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()