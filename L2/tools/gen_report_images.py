"""Результаты обработки тестовых изображений для отчёта (зеркало алгоритмов index.html)."""
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "..", "images")
OUT = os.path.join(HERE, "..", "report")
os.makedirs(OUT, exist_ok=True)


def load_gray(name):
    return Image.open(os.path.join(IMG, f"{name}.png")).convert("L")


def hist_png(img, path, mark=None):
    h = img.histogram()
    top = max(h) or 1
    W, H = 256, 100
    c = Image.new("RGB", (W, H), "#ffffff")
    d = ImageDraw.Draw(c)
    for x in range(256):
        bh = int(h[x] / top * (H - 6))
        d.line([(x, H - 1), (x, H - 1 - bh)], fill="#2f6fdd")
    if mark is not None:
        d.line([(mark, 0), (mark, H - 1)], fill="#e03131", width=1)
    c.save(path)


def linear_contrast(img):
    lo, hi = img.getextrema()
    if hi <= lo:
        return img.copy()
    lut = [max(0, min(255, round((i - lo) * 255 / (hi - lo)))) for i in range(256)]
    return img.point(lut)


def gamma(img, g):
    lut = [round(255 * (i / 255) ** (1 / g)) for i in range(256)]
    return img.point(lut)


def otsu_threshold(hist, total):
    sum_all = sum(i * hist[i] for i in range(256))
    w0 = sum0 = 0
    best, thresh = -1.0, 0
    for t in range(256):
        w0 += hist[t]
        if w0 == 0:
            continue
        w1 = total - w0
        if w1 == 0:
            break
        sum0 += t * hist[t]
        m0, m1 = sum0 / w0, (sum_all - sum0) / w1
        sb = w0 * w1 * (m0 - m1) ** 2
        if sb > best:
            best, thresh = sb, t
    return thresh


def iterative_threshold(hist, total):
    T = round(sum(i * hist[i] for i in range(256)) / total)
    it = 0
    while it < 100:
        s1 = sum(i * hist[i] for i in range(T + 1))
        n1 = sum(hist[: T + 1])
        s2 = sum(i * hist[i] for i in range(T + 1, 256))
        n2 = sum(hist[T + 1 :])
        if n1 == 0 or n2 == 0:
            break
        Tn = round(0.5 * (s1 / n1 + s2 / n2))
        it += 1
        if Tn == T:
            break
        T = Tn
    return T, it


def threshold(img, T):
    lut = [255 if i >= T else 0 for i in range(256)]
    return img.point(lut)


def main():
    results = {}

    # 1. Линейное контрастирование малоконтрастного изображения
    img = load_gray("lowcontrast")
    img.save(os.path.join(OUT, "lowcontrast_src.png"))
    hist_png(img, os.path.join(OUT, "lowcontrast_hist.png"))
    lin = linear_contrast(img)
    lin.save(os.path.join(OUT, "lowcontrast_contrast.png"))
    hist_png(lin, os.path.join(OUT, "lowcontrast_contrast_hist.png"))
    gam = gamma(img, 0.5)
    gam.save(os.path.join(OUT, "lowcontrast_gamma.png"))
    results["lowcontrast"] = (img.getextrema(), lin.getextrema())

    # 2. Пороговая обработка
    for name in ["document", "levels", "noisy", "scene"]:
        img = load_gray(name)
        img.save(os.path.join(OUT, f"{name}_src.png"))
        hist = img.histogram()
        total = img.width * img.height
        t_o = otsu_threshold(hist, total)
        t_i, it = iterative_threshold(hist, total)
        hist_png(img, os.path.join(OUT, f"{name}_hist_otsu.png"), mark=t_o)
        hist_png(img, os.path.join(OUT, f"{name}_hist_iter.png"), mark=t_i)
        threshold(img, t_o).save(os.path.join(OUT, f"{name}_otsu.png"))
        threshold(img, t_i).save(os.path.join(OUT, f"{name}_iter.png"))
        results[name] = (t_o, t_i, it)

    for k, v in results.items():
        print(k, v)


if __name__ == "__main__":
    main()
