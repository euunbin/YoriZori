import pygame
import sys
import random
import time
pygame.font.init()

# 게임 초기화
WIDTH, HEIGHT = 600, 700
BLOCK_SIZE = 40
WHITE, BLACK, GREEN, RED, BLUE, GOLD, CYAN = (255, 255, 255), (0, 0, 0), (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 215, 0), (0, 200, 255)
FONT = pygame.font.SysFont("Malgun Gothic", 36)


SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("5단계 미로 게임")


# 바람 방향 정의
DIRECTIONS = ["UP", "DOWN", "LEFT", "RIGHT"]
wind_direction = random.choice(DIRECTIONS)
last_wind_change_time = time.time()

# 단계별 미로 맵 (0: 길, 1: 벽, 2: 출발점, 3: 도착점)
MAZES = [
    # 1단계
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1],
        [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 3, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ],
    # 2단계
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 3, 1],
        [1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1],
        [1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1],
        [1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1],
        [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    # 3단계
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 3, 1],
        [1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1],
        [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1],
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    # 4단계
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 3, 1],
        [1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
        [1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    # 5단계
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 3, 1],
        [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
        [1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ]
]




# 2단계의 황금색 장애물 좌표 초기화
gold_obstacles = []

# 하늘색 오브젝트 관련 변수
cyan_objects = []
cyan_last_collected = {}  # 하늘색 오브젝트의 마지막 경유 시간


# 현재 단계와 플레이어 위치 초기화
current_level = 0
player_x, player_y = 1, 1


# 바람 방향 업데이트 함수
def change_wind_direction():
    global wind_direction, last_wind_change_time
    if time.time() - last_wind_change_time > 5:
        wind_direction = random.choice(DIRECTIONS)
        last_wind_change_time = time.time()


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



# 시간 관련 변수
time_limit = 60
start_time = time.time()

# 단계 초기화 함수 추가
def reset_level():
    global player_x, player_y, start_time
    player_x, player_y = 1, 1
    start_time = time.time()

# 메시지 표시 함수
def draw_message(text, y_offset):
    # 메시지 크기 조절
    if text == "바람과 반대 방향으로 이동할 수 없습니다!" or"황금 장애물에 닿았습니다! 1단계부터 다시 시작합니다.":
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
    maze = MAZES[current_level]

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
                if current_level >= len(MAZES):
                    game_over = True
                    message = "축하합니다! 모든 단계를 클리어했습니다!"
                    current_level = len(MAZES) - 1  # 인덱스 오류 방지

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
     