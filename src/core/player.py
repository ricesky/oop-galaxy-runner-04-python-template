import os
import pygame

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
PLAYER_SPRITE_PATH = os.path.join(IMAGES_DIR, "player_sprite.png")

class Player:
    def __init__(self, x: float, y: float, speed: float, screen_width: int, lives: int = 3):
        self.x = x
        self.y = y
        self.speed = speed
        self.screen_width = screen_width

        # Ukuran dan warna kapal
        self.width = 40
        self.height = 25
        self.color = (0, 220, 180)

                # --- Sprite & Animation ---
        self.sprite_sheet = pygame.image.load(PLAYER_SPRITE_PATH).convert_alpha()

        # Misal sprite sheet 1 baris, N kolom
        self.frame_count = 4          # sesuaikan dengan file asli
        self.current_frame = 0
        self.frame_duration = 0.1     # detik per frame
        self._animation_timer = 0.0

        self.frames = self._slice_frames()


        # Encapsulated state
        self._score = 0
        self._lives = lives

    # ---------- Properties dengan Validasi ----------

    @property
    def score(self) -> int:
        return self._score

    @score.setter
    def score(self, value: int):
        if value < 0:
            raise ValueError("Score tidak boleh negatif.")
        self._score = int(value)

    @property
    def lives(self) -> int:
        return self._lives

    @lives.setter
    def lives(self, value: int):
        if value < 0:
            raise ValueError("Lives tidak boleh negatif.")
        self._lives = int(value)

    # Convenience methods (opsional, tapi rapi)
    def add_score(self, points: int):
        if points < 0:
            raise ValueError("Penambahan score tidak boleh negatif.")
        self.score = self.score + points

    def lose_life(self, amount: int = 1):
        if amount < 0:
            raise ValueError("Pengurangan nyawa tidak boleh negatif.")
        new_lives = self.lives - amount
        # Jika mau, boleh clamp ke 0
        if new_lives < 0:
            new_lives = 0
        self.lives = new_lives

    def is_dead(self) -> bool:
        return self.lives <= 0

    # ---------- Input & Movement ----------

    def handle_input(self, dt: float):
        keys = pygame.key.get_pressed()
        dx = 0

        if keys[pygame.K_LEFT]:
            dx -= self.speed * dt
        if keys[pygame.K_RIGHT]:
            dx += self.speed * dt

        self.x += dx

        # Batasi supaya tidak keluar layar
        half_w = self.width / 2
        if self.x < half_w:
            self.x = half_w
        if self.x > self.screen_width - half_w:
            self.x = self.screen_width - half_w

    def update(self, dt: float):
        self.handle_input(dt)
        self.update_animation(dt)
    
    def update_animation(self, dt: float):
        """Meng-update frame animasi berdasarkan waktu."""
        # Kalau player diam pun bisa tetap animasi (thruster menyala),
        # tapi kalau mau, bisa dibuat hanya animasi saat bergerak.
        self._animation_timer += dt
        if self._animation_timer >= self.frame_duration:
            self._animation_timer -= self.frame_duration
            self.current_frame = (self.current_frame + 1) % self.frame_count


    # ---------- Collision Helper ----------

    def get_rect(self) -> pygame.Rect:
        rect = pygame.Rect(0, 0, self.width, self.height)
        rect.centerx = int(self.x)
        rect.centery = int(self.y)
        return rect

    def draw(self, surface: pygame.Surface):
        frame = self.frames[self.current_frame]
        rect = frame.get_rect()
        rect.centerx = int(self.x)
        rect.centery = int(self.y)

        surface.blit(frame, rect)
    
    def _slice_frames(self) -> list[pygame.Surface]:
        """Memotong sprite sheet menjadi list frame."""
        sheet_width = self.sprite_sheet.get_width()
        sheet_height = self.sprite_sheet.get_height()

        frame_width = sheet_width // self.frame_count
        frame_height = sheet_height  # 1 baris

        frames: list[pygame.Surface] = []
        for i in range(self.frame_count):
            frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame_surface.blit(
                self.sprite_sheet,
                (0, 0),
                pygame.Rect(i * frame_width, 0, frame_width, frame_height),
            )
            frames.append(frame_surface)

        # Sesuaikan juga ukuran hitbox (rect) dengan ukuran sprite
        self.width = frame_width
        self.height = frame_height

        return frames
