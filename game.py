import pygame
import sys
import random

pygame.init()

# הגדרות חלון
WIDTH, HEIGHT = 400, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spider-Man Climb")

clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

font = pygame.font.SysFont(None, 24)

building_img = pygame.image.load("empire_state.png").convert()
building_img = pygame.transform.scale(building_img, (WIDTH, HEIGHT * 3))
building_height = building_img.get_height()

spiderman_img = pygame.image.load("spiderman.png").convert_alpha()
spiderman_img = pygame.transform.scale(spiderman_img, (40, 40))
spiderman_width, spiderman_height = spiderman_img.get_size()

goblin_img = pygame.image.load("goblin.png").convert_alpha()
goblin_img = pygame.transform.scale(goblin_img, (80, 100))
goblin_width, goblin_height = goblin_img.get_size()

bomb_img = pygame.image.load("bomb.png").convert_alpha()
bomb_img = pygame.transform.scale(bomb_img, (20, 20))
bomb_width, bomb_height = bomb_img.get_size()

# סאונד הגובלין - נטען כ-Sound ונפעיל אותו בערוץ משלו
goblin_sound = pygame.mixer.Sound("goblin_appear.mp3")

# ערוץ לגובלין
goblin_channel = pygame.mixer.Channel(1)

# סאונד טיפוס ספיידרמן
pygame.mixer.music.load("spiderman_climb.mp3")

def run_game():
    spiderman_x = WIDTH // 2 - spiderman_width // 2
    spiderman_y = HEIGHT - spiderman_height - 50
    spiderman_speed = 5

    bombs = []  # רשימת Rectים
    normal_bomb_speed = 4
    normal_bomb_spawn_rate = 30

    distance = 0
    frame_count = 0
    running = True

    normal_bg_scroll_speed = 1
    bg_y = 0

    boss_active = False
    boss_lines_count = 0
    boss_bombs = []  
    boss_gap_width = 60
    boss_triggered_for = set()

    difficulty_factor = 1.0

    # מונה כמה פעמים הבוס הושלם
    boss_encounter_count = 0

    # צבע נוכחי של הפצצות
    # לפני מפגש ראשון: ירוק
    current_color = (0, 255, 0)

    spiderman_quotes = [
        "I got this!",
        "Going up!",
        "Almost there!",
        "Never surrender!",
        "No stopping now!",
        "Up and away!",
        "Watch me climb!",
        "Just keep swinging!",
        "Must go higher!",
        "Can't stop now!"
    ]

    talk_text = ""
    talk_frames_left = 0
    talk_interval = 500
    next_talk_distance = 500

    pygame.mixer.music.play(-1)  # סאונד טיפוס ברצף

    def get_color_for_encounter(encounter_count):
        # לפי encounter_count
        if encounter_count == 0:
            return (0, 255, 0)   # Green
        elif encounter_count == 1:
            return (255, 0, 0)   # Red
        elif encounter_count == 2:
            return (255, 255, 0) # Yellow
        elif encounter_count == 3:
            return (0, 0, 255)   # Blue
        else:
            # 4 ומעלה רנדומלי
            return (random.randint(0,255), random.randint(0,255), random.randint(0,255))

    def spawn_bomb():
        x_pos = random.randint(0, WIDTH - bomb_width)
        y_pos = -bomb_height
        bombs.append(pygame.Rect(x_pos, y_pos, bomb_width, bomb_height))

    def check_collision(spiderman_rect, rect_list):
        for f in rect_list:
            if spiderman_rect.colliderect(f):
                return True
        return False

    def spawn_boss_line(boss_line_speed):
        gap_start = random.randint(0, WIDTH - boss_gap_width)
        line = []
        x = 0
        while x < WIDTH:
            if x < gap_start or x > gap_start + boss_gap_width:
                line.append(pygame.Rect(x, -bomb_height, bomb_width, bomb_height))
            x += bomb_width
        boss_bombs.append(line)

    bomb_speed = normal_bomb_speed
    bomb_spawn_rate = normal_bomb_spawn_rate

    boss_lines_needed = 5
    boss_line_speed_current = 3 * difficulty_factor

    def start_boss(distance):
        nonlocal boss_active, boss_lines_count, boss_bombs, bombs, boss_triggered_for
        nonlocal bomb_speed, bomb_spawn_rate, boss_lines_needed, boss_line_speed_current
        nonlocal difficulty_factor

        boss_active = True
        boss_lines_count = 0
        boss_bombs.clear()
        bombs.clear()
        boss_triggered_for.add(int(distance) // 1000)

        if int(distance) == 10000:
            # בוס מיוחד: 20 שורות פי 2 מהירות
            boss_lines_needed = 20
            boss_line_speed_current = 6
        else:
            boss_lines_needed = 5
            boss_line_speed_current = 3 * difficulty_factor

        spawn_boss_line(boss_line_speed_current)

        pygame.mixer.music.pause()
        # אם זו הפעם הראשונה שהגובלין מגיע:
        if not goblin_channel.get_busy():
            goblin_channel.play(goblin_sound, loops=-1)
        else:
            goblin_channel.unpause()

    while running:
        clock.tick(60)
        frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                goblin_channel.pause()
                running = False
                return int(distance)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and spiderman_x > 0:
            spiderman_x -= spiderman_speed
        if keys[pygame.K_RIGHT] and spiderman_x < WIDTH - spiderman_width:
            spiderman_x += spiderman_speed

        if keys[pygame.K_UP]:
            bg_scroll_speed = normal_bg_scroll_speed * 2 * difficulty_factor
            bomb_speed = normal_bomb_speed * 2 * difficulty_factor
            bomb_spawn_rate = max(1, int(normal_bomb_spawn_rate // 2))
        else:
            bg_scroll_speed = normal_bg_scroll_speed * difficulty_factor
            bomb_speed = normal_bomb_speed * difficulty_factor
            bomb_spawn_rate = int(normal_bomb_spawn_rate)

        distance += bg_scroll_speed

        if distance >= next_talk_distance:
            talk_text = random.choice(spiderman_quotes)
            talk_frames_left = 180
            next_talk_distance += talk_interval

        if not boss_active and int(distance) > 0 and int(distance) % 1000 == 0 and (int(distance) // 1000) not in boss_triggered_for:
            start_boss(distance)

        if not boss_active:
            # מצב רגיל
            for i, f in enumerate(bombs):
                new_rect = pygame.Rect(f.x, f.y + bomb_speed, f.width, f.height)
                bombs[i] = new_rect
                if bombs[i].y > HEIGHT:
                    bombs.pop(i)
                    break

            if frame_count % bomb_spawn_rate == 0:
                spawn_bomb()
        else:
            # מצב בוס
            line_cleared = False
            for line_idx, line in enumerate(boss_bombs):
                new_line = []
                for f in line:
                    new_rect = pygame.Rect(f.x, f.y + boss_line_speed_current, f.width, f.height)
                    new_line.append(new_rect)
                boss_bombs[line_idx] = new_line

                if all(f.y > HEIGHT for f in boss_bombs[line_idx]):
                    boss_bombs.pop(line_idx)
                    boss_lines_count += 1
                    line_cleared = True
                    break

            if line_cleared and boss_lines_count < boss_lines_needed:
                spawn_boss_line(boss_line_speed_current)

            if boss_lines_count >= boss_lines_needed and len(boss_bombs) == 0:
                # הבוס סיים
                boss_active = False
                goblin_channel.pause()
                pygame.mixer.music.unpause()
                difficulty_factor += 0.1
                boss_encounter_count += 1

                # אם עברנו את הגובלין אחרי 10000 מרחק (בוס מיוחד)
                if int(distance) >= 10000 and boss_encounter_count >= 1:
                    # מציג "סרטון" ואז מסיים את המשחק
                    # כאן רק נדגים בהדפסה למסך
                    window.fill(WHITE)
                    end_text = font.render("Now playing final video... The End!", True, BLACK)
                    window.blit(end_text, (WIDTH//2 - end_text.get_width()//2, HEIGHT//2))
                    pygame.display.flip()
                    pygame.time.wait(3000)  # מחכים 3 שניות
                    running = False
                    return int(distance)

                # עדכון הצבע הנוכחי
                current_color = get_color_for_encounter(boss_encounter_count)

        spiderman_rect = pygame.Rect(spiderman_x, spiderman_y, spiderman_width, spiderman_height)

        # בדיקת התנגשות
        if check_collision(spiderman_rect, bombs):
            pygame.mixer.music.stop()
            goblin_channel.pause()
            running = False
        for line in boss_bombs:
            if check_collision(spiderman_rect, line):
                pygame.mixer.music.stop()
                goblin_channel.pause()
                running = False
                break

        bg_y += bg_scroll_speed
        if bg_y > building_height:
            bg_y = 0

        window.blit(building_img, (0, bg_y - building_height))
        window.blit(building_img, (0, bg_y))

        window.blit(spiderman_img, (spiderman_x, spiderman_y))

        # ציור הפצצות בצבע current_color (או רנדומלי אחרי encounter>=4 אבל נבחר כבר)
        def draw_bombs_list(bombs_list):
            for f in bombs_list:
                center_x = f.x + bomb_width // 2
                center_y = f.y + bomb_height // 2
                # אם encounter_count>=4 כבר current_color נקבע כרנדומלי פעם אחת אחרי הבוס האחרון.
                pygame.draw.circle(window, current_color, (center_x, center_y), bomb_width//2 + 2)
                window.blit(bomb_img, (f.x, f.y))

        if not boss_active:
            draw_bombs_list(bombs)
        else:
            for line in boss_bombs:
                draw_bombs_list(line)
            boss_x = WIDTH // 2 - goblin_width // 2
            boss_y = 0
            window.blit(goblin_img, (boss_x, boss_y))

        score_text = font.render(f"Distance: {int(distance)}", True, BLACK)
        window.blit(score_text, (10, 10))

        if talk_frames_left > 0 and talk_text:
            talk_surf = font.render(talk_text, True, BLACK)
            talk_rect = talk_surf.get_rect(midbottom=(spiderman_x + spiderman_width//2, spiderman_y - 10))
            pygame.draw.rect(window, WHITE, talk_rect.inflate(10, 10))
            window.blit(talk_surf, talk_rect)
            talk_frames_left -= 1

        pygame.display.flip()

    return int(distance)

def game_over_screen(final_score):
    game_over = True
    while game_over:
        window.fill(WHITE)
        game_over_text = font.render(f"Game Over! You climbed {final_score} units.", True, BLACK)
        restart_text = font.render("Press R to Restart, Q or ESC to Quit", True, BLACK)

        text_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
        restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))

        window.blit(game_over_text, text_rect)
        window.blit(restart_text, restart_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    return False

def main():
    while True:
        final_score = run_game()
        should_restart = game_over_screen(final_score)
        if not should_restart:
            break

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
