from collections import deque

import pygame
import sys
import random
import time

# 게임 초기화
pygame.init()

# 화면 크기 설정
WIDTH, HEIGHT = 600, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("5단계 미로 게임")

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GOLD = (255, 215, 0)
CYAN = (0, 200, 255)  # 하늘색 오브젝트 색상
MINT = (0, 255, 200)  # 민트색 빙판길 색상

# 블록 크기
BLOCK_SIZE = 40

# 폰트 설정 (한글 지원 폰트 사용)
FONT = pygame.font.SysFont("Malgun Gothic", 36)

# 바람 방향 정의
DIRECTIONS = ["UP", "DOWN", "LEFT", "RIGHT"]
wind_direction = random.choice(DIRECTIONS)
last_wind_change_time = time.time()

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
    if text == "바람과 반대 방향으로 이동할 수 없습니다!" or "황금 장애물에 닿았습니다! 1단계부터 다시 시작합니다.":
        font = pygame.font.SysFont("Malgun Gothic", 25)  # 글씨 크기 25
    else:
        font = pygame.font.SysFont("Malgun Gothic", 36)  # 기본 글씨 크기

    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, y_offset))
    SCREEN.blit(text_surface, text_rect)


# 남은 시간 표시 함수
def draw_timer():
    global start_time
    elapsed_time = time.time() - start_time
    remaining_time = max(0, int(time_limit - elapsed_time))
    timer_text = FONT.render(f"남은 시간: {remaining_time}초", True, WHITE)
    SCREEN.blit(timer_text, (WIDTH - 250, 30))
    return remaining_time


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
            player_x, player_y = 1, 1
            lives = 3
            gold_obstacles = []
            message = "황금 장애물에 닿았습니다! 1단계부터 다시 시작합니다."
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
                message = "하늘색 오브젝트 경유! 5초 추가!"
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

                else:
                    # 다음 단계로 초기화
                    player_x, player_y = 1, 1
                    path = []
                    moving = False
                    message = f"다음 단계로 이동합니다: {current_level + 1} 단계"
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

    # 미로 그리기
    for row in range(len(maze)):
        for col in range(len(maze[row])):
            color = WHITE
            if maze[row][col] == 1:
                color = BLACK
            elif maze[row][col] == 2:
                color = GREEN
            elif maze[row][col] == 3:
                color = RED
            pygame.draw.rect(SCREEN, color, (col * BLOCK_SIZE, row * BLOCK_SIZE + 200, BLOCK_SIZE, BLOCK_SIZE))

    # 용암(빨간 오브젝트) 그리기
    if current_level == 4:  # 5단계 인덱스는 4
        for (lx, ly) in lava_objects:
            pygame.draw.rect(SCREEN, RED, (lx * BLOCK_SIZE, ly * BLOCK_SIZE + 200, BLOCK_SIZE, BLOCK_SIZE))

    # 게임 루프 내 연기 이동 및 표시
    if current_level == 4:  # 5단계에서만 연기 표시
        draw_smoke()

    # 빙판길 그리기 (4단계 전용)
    if current_level == 3:
        for (ix, iy) in ice_paths:
            pygame.draw.rect(SCREEN, MINT, (ix * BLOCK_SIZE, iy * BLOCK_SIZE + 200, BLOCK_SIZE, BLOCK_SIZE))

    # 하늘색 오브젝트 그리기
    if current_level == 2:
        for (cx, cy) in cyan_objects:
            pygame.draw.rect(SCREEN, CYAN, (cx * BLOCK_SIZE, cy * BLOCK_SIZE + 200, BLOCK_SIZE, BLOCK_SIZE))

    # 황금색 장애물 그리기
    if current_level == 1:
        for (gx, gy) in gold_obstacles:
                    pygame.draw.rect(SCREEN, GOLD, (gx * BLOCK_SIZE, gy * BLOCK_SIZE + 200, BLOCK_SIZE, BLOCK_SIZE))

    # 경로 그리기
    if len(draw_path) > 1:
        pygame.draw.lines(SCREEN, GREEN, False, draw_path, 3)

    # 플레이어 그리기
    if not game_over:
        pygame.draw.rect(SCREEN, BLUE, (player_x * BLOCK_SIZE, player_y * BLOCK_SIZE + 200, BLOCK_SIZE, BLOCK_SIZE))

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