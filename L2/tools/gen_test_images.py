"""Генерация тестовой базы изображений для лабораторной работы 2."""
import os
import random
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
os.makedirs(OUT, exist_ok=True)
random.seed(42)

SIZE = 256


def add_noise(img, sigma=6):
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            v = px[x, y] + random.gauss(0, sigma)
            px[x, y] = max(0, min(255, int(round(v))))
    return img


# 1. «Документ» — бимодальная гистограмма (текст на светлом фоне)
def make_document():
    img = Image.new("L", (SIZE, SIZE), 235)
    d = ImageDraw.Draw(img)
    y = 24
    while y < SIZE - 16:
        x = 20
        while x < SIZE - 30:
            w = random.randint(12, 46)
            if random.random() < 0.75:
                d.rectangle([x, y, x + w, y + 7], fill=30)
            x += w + random.randint(6, 14)
        y += random.randint(16, 24)
    add_noise(img, 5)
    return img


# 2. Малоконтрастное изображение — сцена, сжатая в диапазон [100; 150]
def make_lowcontrast():
    img = Image.new("L", (SIZE, SIZE), 0)
    d = ImageDraw.Draw(img)
    for i, r in enumerate(range(200, 10, -14)):
        d.ellipse([128 - r, 128 - r, 128 + r, 128 + r], fill=40 + i * 12)
    d.rectangle([0, 190, SIZE, SIZE], fill=210)
    d.rectangle([150, 60, 220, 190], fill=150)
    img = img.filter(ImageFilter.GaussianBlur(3))
    px = img.load()
    for y in range(SIZE):
        for x in range(SIZE):
            px[x, y] = int(100 + (px[x, y] / 255) * 50)  # сжатие в [100; 150]
    return img


# 3. Зашумлённое изображение с перепадами яркости
def make_noisy():
    img = Image.new("L", (SIZE, SIZE), 0)
    d = ImageDraw.Draw(img)
    for i in range(8):
        for j in range(8):
            v = 40 + ((i + j) % 2) * 150
            d.rectangle([i * 32, j * 32, i * 32 + 31, j * 32 + 31], fill=v)
    add_noise(img, 25)
    return img


# 4. Многоуровневое изображение — гистограмма с несколькими пиками
def make_levels():
    img = Image.new("L", (SIZE, SIZE), 0)
    d = ImageDraw.Draw(img)
    bands = [(0, 60, 40), (60, 120, 110), (120, 180, 160), (180, 256, 215)]
    for x0, x1, v in bands:
        d.rectangle([x0, 0, x1 - 1, 170], fill=v)
    d.ellipse([80, 130, 176, 226], fill=75)
    d.rectangle([0, 170, 255, 255], fill=185)
    add_noise(img, 4)
    return img


# 5. Сцена с доминирующей средней модой: яркая полоса 240 (~6 %),
# широкая равномерная мода фона 130..170 (~88 %), тёмные объекты 40 (~6 %).
# Средняя яркость ~= центру моды фона -> итеративный метод расщепляет
# фон пополам и теряет объекты, а метод Оцу выделяет тёмные объекты.
def make_scene():
    img = Image.new("L", (SIZE, SIZE), 0)
    px = img.load()
    for y in range(SIZE):                 # широкий равномерный фон
        for x in range(SIZE):
            px[x, y] = random.randint(130, 170)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, SIZE, 16], fill=240)  # яркая полоса (небо)
    for _ in range(6):
        r = random.randint(13, 16)
        x = random.randint(r, SIZE - r)
        y = random.randint(60, SIZE - r)
        d.ellipse([x - r, y - r, x + r, y + r], fill=40)  # объекты (камни)
    add_noise(img, 4)
    return img


def main():
    makers = {
        "document": make_document,
        "lowcontrast": make_lowcontrast,
        "noisy": make_noisy,
        "levels": make_levels,
        "scene": make_scene,
    }
    for name, fn in makers.items():
        path = os.path.join(OUT, f"{name}.png")
        fn().save(path)
        print("saved", path)


if __name__ == "__main__":
    main()
