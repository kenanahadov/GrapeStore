
from pathlib import Path
import re
from decimal import Decimal

from django.core.management.base import BaseCommand
from store.models import Product, ProductImage

IMAGE_DIR = Path(__file__).resolve().parent.parent.parent / "static" / "store" / "products"
RE_CLEAN_PAREN = re.compile(r"\s*\(\d+\)$")
CATEGORY_PRICING = {
    "macbook": Decimal("1299.00"),
    "laptop": Decimal("799.00"),
    "airpods max": Decimal("479.00"),
    "airpods": Decimal("189.00"),
    "mouse": Decimal("49.00"),
    "keyboard": Decimal("119.00"),
    "monitor": Decimal("299.00"),
    "speaker": Decimal("149.00"),
}

def _base_name(filename: str) -> str:
    name = Path(filename).stem
    name = RE_CLEAN_PAREN.sub("", name)
    return name.replace("...", "").strip()

def _guess_price(title: str) -> Decimal:
    lower = title.lower()
    for key, price in CATEGORY_PRICING.items():
        if key in lower:
            return price
    return Decimal("99.00")

def _build_description(title: str) -> str:
    cleaned = title.replace("...", "")
    segments = [seg.strip() for seg in re.split(r"[,.]", cleaned) if seg.strip()]
    bullets = "\n".join(f" - {seg}" for seg in segments)
    return (
        f"{cleaned}\n\n"
        f"**Highlights**\n{bullets}\n\n"
        "Crafted for everyday excellence and built to last, this item combines reliable "
        "performance with sleek aesthetics—perfect for work, play, and everything in between."
    )

class Command(BaseCommand):
    help = "Add or refresh products based on images in static/store/products"

    def add_arguments(self, parser):
        parser.add_argument("--refresh", action="store_true", help="Rebuild products from scratch")

    def handle(self, *args, **options):
        refresh = options["refresh"]
        if not IMAGE_DIR.exists():
            self.stderr.write(self.style.ERROR(f"Directory {IMAGE_DIR} not found"))
            return

        groups = {}
        for img in IMAGE_DIR.iterdir():
            if img.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
                continue
            title = _base_name(img.name)
            groups.setdefault(title, []).append(img)

        if refresh:
            auto = Product.objects.filter(description__icontains="Crafted for everyday excellence")
            count = auto.count()
            auto.delete()
            self.stdout.write(self.style.WARNING(f"Deleted {count} auto‑generated products"))

        created = 0
        for title, paths in groups.items():
            product, _ = Product.objects.get_or_create(
                name=title,
                defaults={
                    "description": _build_description(title),
                    "price": _guess_price(title),
                },
            )
            for img_path in paths:
                ProductImage.objects.get_or_create(
                    product=product,
                    url=f"/static/store/products/{img_path.name}",
                )
            created += 1
        self.stdout.write(self.style.SUCCESS(f"Processed {created} products"))
