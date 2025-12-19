import pygame
import random
import time

# ================== CONFIG ==================
WIDTH, HEIGHT = 800, 800
FPS = 60

DIRECTIONS = ["UP", "DOWN", "LEFT", "RIGHT"]

VEHICLE_SPEED = 2
AMBULANCE_SPEED = 3

MIN_GREEN = 3
MAX_GREEN = 6

# ================== PATHS ==================
BG_IMAGE = "images/intersection.png"

SIGNAL_IMAGES = {
    "RED": "images/signal/red.png",
    "GREEN": "images/signal/green.png"
}

VEHICLE_IMAGES = {
    "UP": "images/vehicles/up/car.png",
    "DOWN": "images/vehicles/down/car.png",
    "LEFT": "images/vehicles/left/car.png",
    "RIGHT": "images/vehicles/right/car.png"
}

AMBULANCE_IMAGE = "images/vehicles/up/ambulance.png"

SIGNAL_POS = {
    "UP": (380, 290),
    "DOWN": (380, 470),
    "LEFT": (290, 380),
    "RIGHT": (470, 380)
}

# ================== INIT ==================
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Traffic Controller (AI)")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# ================== HELPERS ==================
def load_image(path, size):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        surf = pygame.Surface(size)
        surf.fill((200, 200, 200))
        return surf

# ================== LOAD ASSETS ==================
bg = load_image(BG_IMAGE, (WIDTH, HEIGHT))
signal_imgs = {
    k: load_image(v, (30, 30)) for k, v in SIGNAL_IMAGES.items()
}
vehicle_imgs = {
    d: load_image(VEHICLE_IMAGES[d], (40, 25)) for d in DIRECTIONS
}
ambulance_img = load_image(AMBULANCE_IMAGE, (50, 30))

# ================== VEHICLE ==================
class Vehicle:
    def __init__(self, direction, ambulance=False):
        self.direction = direction
        self.is_ambulance = ambulance
        self.speed = AMBULANCE_SPEED if ambulance else VEHICLE_SPEED
        self.image = ambulance_img if ambulance else vehicle_imgs[direction]

        if direction == "UP": self.x, self.y = 390, 820
        if direction == "DOWN": self.x, self.y = 360, -40
        if direction == "LEFT": self.x, self.y = 820, 360
        if direction == "RIGHT": self.x, self.y = -40, 390

    def move(self):
        if self.direction == "UP": self.y -= self.speed
        if self.direction == "DOWN": self.y += self.speed
        if self.direction == "LEFT": self.x -= self.speed
        if self.direction == "RIGHT": self.x += self.speed

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

# ================== CONTROLLER ==================
class TrafficController:
    def __init__(self):
        self.signals = {d: "RED" for d in DIRECTIONS}
        self.current_green = "UP"
        self.signals[self.current_green] = "GREEN"

        self.vehicles = {d: [] for d in DIRECTIONS}
        self.last_switch = time.time()
        self.green_time = MIN_GREEN

    def spawn_vehicle(self):
        d = random.choice(DIRECTIONS)
        is_amb = random.random() < 0.12
        self.vehicles[d].append(Vehicle(d, is_amb))

    def detect_ambulance(self):
        for d in DIRECTIONS:
            for v in self.vehicles[d]:
                if v.is_ambulance:
                    return d
        return None

    def force_green(self, d):
        for k in DIRECTIONS:
            self.signals[k] = "RED"
        self.signals[d] = "GREEN"
        self.current_green = d
        self.last_switch = time.time()

    def update_signals(self):
        amb_dir = self.detect_ambulance()
        if amb_dir:
            self.force_green(amb_dir)
            return

        if time.time() - self.last_switch > self.green_time:
            self.signals[self.current_green] = "RED"
            self.current_green = max(self.vehicles, key=lambda x: len(self.vehicles[x]))
            self.signals[self.current_green] = "GREEN"
            self.green_time = min(MAX_GREEN, MIN_GREEN + len(self.vehicles[self.current_green]) * 0.5)
            self.last_switch = time.time()

    def move_vehicles(self):
        for d in DIRECTIONS:
            for v in self.vehicles[d][:]:
                if self.signals[d] == "GREEN" or v.is_ambulance:
                    v.move()
                if v.x < -60 or v.x > WIDTH+60 or v.y < -60 or v.y > HEIGHT+60:
                    self.vehicles[d].remove(v)

    def draw_vehicles(self):
        for d in DIRECTIONS:
            for v in self.vehicles[d]:
                v.draw()

    def draw_signals(self):
        for d in DIRECTIONS:
            screen.blit(signal_imgs[self.signals[d]], SIGNAL_POS[d])

# ================== MAIN ==================
controller = TrafficController()
spawn_tick = 0
running = True

while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    spawn_tick += 1
    if spawn_tick > 35:
        controller.spawn_vehicle()
        spawn_tick = 0

    controller.update_signals()
    controller.move_vehicles()

    screen.blit(bg, (0, 0))
    controller.draw_vehicles()
    controller.draw_signals()

    info = font.render(f"GREEN : {controller.current_green}", True, (0,0,0))
    screen.blit(info, (10, 10))

    pygame.display.flip()

pygame.quit()
