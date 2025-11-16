# oop-galaxy-runner-04-python

## Capaian Pembelajaran

Setelah menyelesaikan seluruh tahapan, mahasiswa diharapkan mampu:

1. Memodelkan permainan 2D sederhana menggunakan **pemrograman berorientasi objek** (class, object, composition, encapsulation, inheritance, polymorphism) di Python.
2. Menggunakan **PyGame** untuk membangun game 2D dengan beberapa komponen: player, musuh (enemy), background, skor, dan UI dasar.
3. Menerapkan **multimedia** (gambar, sprite animation, suara) di dalam game.
4. Mengelola **beberapa screen** (main menu, game screen, high score) menggunakan Screen Manager berbasis OOP.
5. Menerapkan **perilaku AI sederhana** pada musuh (enemy) dan mengatur tingkat kesulitan permainan.

---

## Lingkungan Pengembangan

1. Platform: Python **3.12+** (boleh 3.13 selama PyGame berjalan)
2. Bahasa: Python
3. Editor/IDE yang disarankan:

   * VS Code + Python Extension
   * Terminal
4. Library:

   * `pygame 2.6.1`
   * `pytest`

---

## Cara Menjalankan Project

```bash
python -m src.main
```

---

# Tahap 4 — Screen Manager & Multi Screen (Main Menu, Game, High Score)

**Tujuan Tahap 4**

1. Mahasiswa memahami konsep **Screen / Scene** pada game:

   * Main Menu Screen
   * Game Screen
   * High Score Screen (sementara dummy saja)
2. Mahasiswa dapat mengimplementasikan **Screen Manager** sederhana:

   * `current_screen` + metode `switch_to(...)`
3. Mahasiswa dapat membuat **Button sederhana** di PyGame untuk berpindah screen.

---

## 0. Struktur Direktori Baru

Kita tambahkan beberapa file baru agar arsitektur game rapi:

```text
src/
├─ main.py
├─ core/
│  ├─ game.py          # tetap dipakai sebagai "world" untuk GameScreen
│  ├─ player.py
│  ├─ enemy.py
│  └─ starfield.py
├─ ui/
│  ├─ __init__.py
│  └─ button.py        # tombol sederhana (UI)
└─ screens/
   ├─ __init__.py
   ├─ base.py          # BaseScreen (abstract)
   ├─ main_menu.py     # MainMenuScreen
   ├─ game_screen.py   # GameScreen (pakai class Game dari core.game)
   └─ high_score.py    # HighScoreScreen (dummy dulu)
```

> `__init__.py` boleh kosong, hanya penanda package.

---

## 1. Membuat Button Sederhana (UI)

Sebelum membuat screen, kita butuh komponen **Button** yang bisa:

* menggambar kotak dengan label teks,
* mengetahui apakah diklik oleh mouse.

---

### 1.1. Buat folder & file UI

**File baru:** `src/ui/button.py`

Isi dengan class `Button` sederhana seperti ini:

```python
import pygame


class Button:
    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font,
                 bg_color=(70, 70, 160), hover_color=(100, 100, 220), text_color=(255, 255, 255)):
        self.rect = rect
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color

    def is_hovered(self, mouse_pos) -> bool:
        return self.rect.collidepoint(mouse_pos)

    def draw(self, surface: pygame.Surface):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.is_hovered(mouse_pos) else self.bg_color

        pygame.draw.rect(surface, color, self.rect, border_radius=8)

        label = self.font.render(self.text, True, self.text_color)
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Return True jika tombol diklik (Mouse Left)."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False
```

---

## 2. BaseScreen dan ScreenManager

Kita ingin tiap screen punya pola yang sama:

* `handle_event(event)`
* `update(dt)`
* `draw(surface)`

Jadi kita buat:

* `BaseScreen` (kelas dasar abstrak)
* `ScreenManager` (mengelola `current_screen`)

---

### 2.1. BaseScreen

**File baru:** `src/screens/base.py`

```python
import abc
import pygame


class BaseScreen(abc.ABC):
    def __init__(self, manager, screen_width: int, screen_height: int):
        self.manager = manager
        self.screen_width = screen_width
        self.screen_height = screen_height

    @abc.abstractmethod
    def handle_event(self, event: pygame.event.Event):
        ...

    @abc.abstractmethod
    def update(self, dt: float):
        ...

    @abc.abstractmethod
    def draw(self, surface: pygame.Surface):
        ...
```

---

### 2.2. ScreenManager

**File baru:** `src/screen_manager.py`

```python
import pygame


class ScreenManager:
    def __init__(self, initial_screen):
        self.current_screen = initial_screen

    def switch_to(self, new_screen):
        self.current_screen = new_screen

    def handle_event(self, event: pygame.event.Event):
        self.current_screen.handle_event(event)

    def update(self, dt: float):
        self.current_screen.update(dt)

    def draw(self, surface: pygame.Surface):
        self.current_screen.draw(surface)
```

---

## 3. Main Menu Screen

Main menu akan punya:

* judul “Galaxy Runner”
* tombol:

  * `Start Game`
  * `High Score`
  * `Quit`

Klik tombol akan memanggil `manager.switch_to(...)` ke screen lain, atau keluar game.

---

### 3.1. Buat `MainMenuScreen`

**File baru:** `src/screens/main_menu.py`

```python
import pygame
from .base import BaseScreen
from ..ui.button import Button


class MainMenuScreen(BaseScreen):
    def __init__(self, manager, screen_width: int, screen_height: int):
        super().__init__(manager, screen_width, screen_height)

        self.background_color = (10, 10, 40)

        self.title_font = pygame.font.SysFont(None, 64)
        self.button_font = pygame.font.SysFont(None, 32)

        # Posisi tombol
        button_width = 220
        button_height = 50
        center_x = screen_width // 2
        start_y = screen_height // 2 - 40

        self.start_button = Button(
            pygame.Rect(center_x - button_width // 2, start_y, button_width, button_height),
            "Start Game",
            self.button_font,
        )

        self.highscore_button = Button(
            pygame.Rect(center_x - button_width // 2, start_y + 70, button_width, button_height),
            "High Score",
            self.button_font,
        )

        self.quit_button = Button(
            pygame.Rect(center_x - button_width // 2, start_y + 140, button_width, button_height),
            "Quit",
            self.button_font,
        )

    def handle_event(self, event: pygame.event.Event):
        if self.start_button.handle_event(event):
            from .game_screen import GameScreen
            new_screen = GameScreen(self.manager, self.screen_width, self.screen_height)
            self.manager.switch_to(new_screen)

        if self.highscore_button.handle_event(event):
            from .high_score import HighScoreScreen
            new_screen = HighScoreScreen(self.manager, self.screen_width, self.screen_height)
            self.manager.switch_to(new_screen)

        if self.quit_button.handle_event(event):
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, dt: float):
        # Main menu tidak punya animasi khusus, boleh dikosongkan.
        pass

    def draw(self, surface: pygame.Surface):
        surface.fill(self.background_color)

        # Judul
        title_surf = self.title_font.render("Galaxy Runner", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 120))
        surface.blit(title_surf, title_rect)

        # Tombol
        self.start_button.draw(surface)
        self.highscore_button.draw(surface)
        self.quit_button.draw(surface)
```

---

## 4. GameScreen: Membungkus `core.Game` jadi Screen

Sekarang kita tidak ingin `main.py` langsung membuat `Game` (dari `core.game`) dan menjalankannya.
Kita ingin `Game` itu dikelola oleh `GameScreen`, yang nantinya bisa:

* kembali ke Main Menu,
* pindah ke High Score saat Game Over, dll.

---

### 4.1. Buat `GameScreen`

**File baru:** `src/screens/game_screen.py`

```python
import pygame
from .base import BaseScreen
from ..core.game import Game
from ..ui.button import Button


class GameScreen(BaseScreen):
    def __init__(self, manager, screen_width: int, screen_height: int):
        super().__init__(manager, screen_width, screen_height)

        self.game = Game(screen_width, screen_height)

        # Tombol Back to Menu (misal di pojok kanan atas)
        self.button_font = pygame.font.SysFont(None, 24)
        self.back_button = Button(
            pygame.Rect(screen_width - 150, 10, 140, 40),
            "Back to Menu",
            self.button_font,
            bg_color=(80, 80, 80),
            hover_color=(120, 120, 120),
        )

    def handle_event(self, event: pygame.event.Event):
        # Forward event ke Game jika suatu saat perlu (misal pause dsb.)
        self.game.handle_event(event)

        if self.back_button.handle_event(event):
            from .main_menu import MainMenuScreen
            new_screen = MainMenuScreen(self.manager, self.screen_width, self.screen_height)
            self.manager.switch_to(new_screen)

    def update(self, dt: float):
        self.game.update(dt)

    def draw(self, surface: pygame.Surface):
        self.game.draw(surface)
        self.back_button.draw(surface)
```

> Di sini `Game` (Tahap 1–3) **tidak diubah**, hanya “dibungkus” di dalam `GameScreen`.

---

## 5. HighScoreScreen (Dummy Sementara)

Supaya flow Main Menu → High Score → Back to Menu jalan, kita buat screen sederhana dulu.
Nanti Tahap 5 bisa diisi dengan penyimpanan skor ke file / JSON.

---

### 5.1. Buat `HighScoreScreen`

**File baru:** `src/screens/high_score.py`

```python
import pygame
from .base import BaseScreen
from ..ui.button import Button


class HighScoreScreen(BaseScreen):
    def __init__(self, manager, screen_width: int, screen_height: int):
        super().__init__(manager, screen_width, screen_height)

        self.background_color = (20, 10, 40)
        self.title_font = pygame.font.SysFont(None, 48)
        self.text_font = pygame.font.SysFont(None, 28)

        self.back_button = Button(
            pygame.Rect(20, screen_height - 70, 160, 40),
            "Back to Menu",
            self.text_font,
        )

        # Untuk sementara, high score masih dummy text
        self.dummy_scores = ["1. AAA - 1230", "2. BBB - 900", "3. CCC - 750"]

    def handle_event(self, event: pygame.event.Event):
        if self.back_button.handle_event(event):
            from .main_menu import MainMenuScreen
            new_screen = MainMenuScreen(self.manager, self.screen_width, self.screen_height)
            self.manager.switch_to(new_screen)

    def update(self, dt: float):
        pass

    def draw(self, surface: pygame.Surface):
        surface.fill(self.background_color)

        title_surf = self.title_font.render("High Scores", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, 80))
        surface.blit(title_surf, title_rect)

        y = 150
        for line in self.dummy_scores:
            text_surf = self.text_font.render(line, True, (230, 230, 230))
            text_rect = text_surf.get_rect(center=(self.screen_width // 2, y))
            surface.blit(text_surf, text_rect)
            y += 40

        self.back_button.draw(surface)
```

---

## 6. Mengubah `main.py` untuk Menggunakan ScreenManager

Sampai Tahap 3, `main.py` langsung membuat `Game` dan menjalankan game loop.
Sekarang kita ubah supaya:

* Inisialisasi `MainMenuScreen`,
* Bungkus dengan `ScreenManager`,
* Loop utama selalu memanggil `manager.handle_event/update/draw`.

---

### 6.1. Update `src/main.py`

**File:** `src/main.py`

Isi lama (contoh):

```python
import pygame
from .core.game import Game


def main():
    pygame.init()

    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Galaxy Runner - Stage 1")

    clock = pygame.time.Clock()
    game = Game(screen_width, screen_height)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_event(event)

        game.update(dt)
        game.draw(screen)
        pygame.display.flip()

    pygame.quit()
```

Ubah menjadi (pakai ScreenManager + MainMenuScreen):

```python
import pygame
from .screen_manager import ScreenManager
from .screens.main_menu import MainMenuScreen


def main():
    pygame.init()

    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Galaxy Runner")

    clock = pygame.time.Clock()

    # Buat screen awal (Main Menu) dan ScreenManager
    main_menu = MainMenuScreen(None, screen_width, screen_height)
    manager = ScreenManager(main_menu)
    # Inject manager ke screen (agar bisa switch)
    main_menu.manager = manager

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                manager.handle_event(event)

        manager.update(dt)
        manager.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
```

> Ketika `MainMenuScreen` membuat `GameScreen` / `HighScoreScreen`, ia akan mengirim `self.manager` ke screen baru, jadi setiap screen punya akses ke `ScreenManager`.

---

## 7. Menjalankan Tahap 4

Sekarang jalankan lagi:

```bash
python -m src.main
```

Flow yang diharapkan:

1. Program membuka **Main Menu**:

   * Judul “Galaxy Runner”.
   * Tiga tombol: Start Game, High Score, Quit.
2. Klik **Start Game** → masuk ke **GameScreen**, menjalankan Galaxy Runner seperti Tahap 3 (enemy, score, lives, sprite, sound).
3. Di dalam game, tombol **Back to Menu** akan kembali ke Main Menu.
4. Dari Main Menu → klik **High Score** → masuk ke HighScoreScreen (dummy).
5. Di HighScoreScreen → klik **Back to Menu** → kembali Main Menu.

---