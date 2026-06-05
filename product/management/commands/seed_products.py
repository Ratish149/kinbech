from django.core.management.base import BaseCommand
from django.utils.text import slugify

from product.models import Category, Product, Subcategory


class Command(BaseCommand):
    help = "Seeds the database with categories, subcategories, and products."

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # 1. Define categories and their subcategories
        categories_data = [
            {
                "slug": "fresh-meat",
                "name": "Fresh Meat",
                "subs": [
                    {"slug": "mutton", "name": "Mutton"},
                    {"slug": "chicken", "name": "Chicken"},
                    {"slug": "buff", "name": "Buff"},
                    {"slug": "pork", "name": "Pork"},
                ],
            },
            {
                "slug": "processed-meat",
                "name": "Processed Meat",
                "subs": [
                    {"slug": "sausages", "name": "Sausages"},
                    {"slug": "salami", "name": "Salami"},
                    {"slug": "ham", "name": "Ham"},
                    {"slug": "bacon", "name": "Bacon"},
                ],
            },
            {
                "slug": "cooked-meat",
                "name": "Cooked Meat",
                "subs": [
                    {"slug": "ready-curry", "name": "Ready Curry"},
                    {"slug": "kebabs", "name": "Kebabs"},
                    {"slug": "momo", "name": "Momo"},
                ],
            },
            {
                "slug": "sukuti",
                "name": "Sukuti & Dry",
                "subs": [
                    {"slug": "buff-sukuti", "name": "Buff Sukuti"},
                    {"slug": "mutton-sukuti", "name": "Mutton Sukuti"},
                    {"slug": "spicy-sukuti", "name": "Spicy Sukuti"},
                ],
            },
            {
                "slug": "vegetables",
                "name": "Vegetables",
                "subs": [
                    {"slug": "leafy", "name": "Leafy Greens"},
                    {"slug": "root", "name": "Root Vegetables"},
                    {"slug": "seasonal", "name": "Seasonal"},
                ],
            },
            {
                "slug": "farm-produce",
                "name": "Farm Produce",
                "subs": [
                    {"slug": "dairy", "name": "Dairy"},
                    {"slug": "eggs", "name": "Eggs"},
                    {"slug": "honey", "name": "Honey & Ghee"},
                ],
            },
        ]

        # Create Categories and Subcategories
        category_cache = {}
        subcategory_cache = {}

        for cat_data in categories_data:
            category, _ = Category.objects.get_or_create(
                slug=cat_data["slug"], defaults={"name": cat_data["name"]}
            )
            category_cache[cat_data["slug"]] = category

            for sub_data in cat_data["subs"]:
                subcategory, _ = Subcategory.objects.get_or_create(
                    slug=sub_data["slug"],
                    category=category,
                    defaults={"name": sub_data["name"]},
                )
                subcategory_cache[sub_data["slug"]] = subcategory

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded {Category.objects.count()} categories and {Subcategory.objects.count()} subcategories."
            )
        )

        # 2. Define products data
        def img(q):
            return f"https://images.unsplash.com/{q}?auto=format&fit=crop&w=900&q=70"

        products_data = [
            {
                "name": "Fresh Mutton Curry Cut",
                "category": "fresh-meat",
                "subcategory": "mutton",
                "price": 1450.00,
                "market_price": 1600.00,
                "image": img("photo-1602471122917-3b938cad4c89"),
                "unit": "1 kg",
                "stock": 30,
                "description": "Tender, hand-cut mutton sourced from highland farms in Nepal.",
            },
            {
                "name": "Country Chicken Whole",
                "category": "fresh-meat",
                "subcategory": "chicken",
                "price": 620.00,
                "image": img("photo-1604908176997-125f25cc6f3d"),
                "unit": "1 kg",
                "stock": 50,
                "description": "Free-range country chicken raised without antibiotics.",
            },
            {
                "name": "Boneless Buff",
                "category": "fresh-meat",
                "subcategory": "buff",
                "price": 780.00,
                "image": img("photo-1588347818111-a3a2bb98ba0e"),
                "unit": "1 kg",
                "stock": 25,
                "description": "Lean boneless buff, perfect for curries and stir-fries.",
            },
            {
                "name": "Pork Belly Slices",
                "category": "fresh-meat",
                "subcategory": "pork",
                "price": 990.00,
                "image": img("photo-1607623814075-e51df1bdc82f"),
                "unit": "500 g",
                "stock": 18,
                "description": "Fresh pork belly cut into perfect slices.",
            },
            {
                "name": "Pork Sausage Pack",
                "category": "processed-meat",
                "subcategory": "sausages",
                "price": 540.00,
                "image": img("photo-1601001815853-3835274403b3"),
                "unit": "6 pcs",
                "stock": 40,
                "description": "Smoky pork sausages, ready to grill.",
            },
            {
                "name": "Italian Salami",
                "category": "processed-meat",
                "subcategory": "salami",
                "price": 720.00,
                "market_price": 820.00,
                "image": img("photo-1599583863916-e06c29087f51"),
                "unit": "200 g",
                "stock": 22,
                "description": "Aged Italian-style salami with delicate spices.",
            },
            {
                "name": "Smoked Ham",
                "category": "processed-meat",
                "subcategory": "ham",
                "price": 880.00,
                "image": img("photo-1607103058027-4c5dbdf73a40"),
                "unit": "250 g",
                "stock": 14,
                "description": "Hardwood smoked ham, sliced thin.",
            },
            {
                "name": "Crispy Bacon Strips",
                "category": "processed-meat",
                "subcategory": "bacon",
                "price": 640.00,
                "image": img("photo-1528607929212-2636ec44253e"),
                "unit": "200 g",
                "stock": 30,
                "description": "Cured and smoked bacon strips ready to pan-fry.",
            },
            {
                "name": "Ready Chicken Curry",
                "category": "cooked-meat",
                "subcategory": "ready-curry",
                "price": 420.00,
                "image": img("photo-1604908176997-431a4d0a8b7c"),
                "unit": "500 g",
                "stock": 24,
                "description": "Home-style chicken curry, heat and serve.",
            },
            {
                "name": "Seekh Kebabs",
                "category": "cooked-meat",
                "subcategory": "kebabs",
                "price": 380.00,
                "image": img("photo-1626776876729-bab4369a5a5a"),
                "unit": "6 pcs",
                "stock": 30,
                "description": "Charcoal-grilled seekh kebabs.",
            },
            {
                "name": "Buff Momo (Frozen)",
                "category": "cooked-meat",
                "subcategory": "momo",
                "price": 320.00,
                "image": img("photo-1496116218417-1a781b1c416c"),
                "unit": "20 pcs",
                "stock": 60,
                "description": "Handmade buff momos, freezer to steamer.",
            },
            {
                "name": "Classic Buff Sukuti",
                "category": "sukuti",
                "subcategory": "buff-sukuti",
                "price": 1200.00,
                "image": img("photo-1606851094291-6efae152bb87"),
                "unit": "250 g",
                "stock": 18,
                "description": "Traditional Nepali dried buff, perfectly seasoned.",
            },
            {
                "name": "Mutton Sukuti",
                "category": "sukuti",
                "subcategory": "mutton-sukuti",
                "price": 1650.00,
                "image": img("photo-1604908176997-1f8c6f4f0e0f"),
                "unit": "250 g",
                "stock": 12,
                "description": "Premium mountain mutton sukuti.",
            },
            {
                "name": "Spicy Achari Sukuti",
                "category": "sukuti",
                "subcategory": "spicy-sukuti",
                "price": 1100.00,
                "market_price": 1300.00,
                "image": img("photo-1625938144755-652e08e359b7"),
                "unit": "200 g",
                "stock": 20,
                "description": "Tangy, fiery achari sukuti.",
            },
            {
                "name": "Organic Spinach",
                "category": "vegetables",
                "subcategory": "leafy",
                "price": 80.00,
                "image": img("photo-1576045057995-568f588f82fb"),
                "unit": "500 g",
                "stock": 80,
                "description": "Freshly harvested organic spinach.",
            },
            {
                "name": "Mountain Potatoes",
                "category": "vegetables",
                "subcategory": "root",
                "price": 120.00,
                "image": img("photo-1518977676601-b53f82aba655"),
                "unit": "1 kg",
                "stock": 100,
                "description": "Earthy mountain potatoes from Mustang.",
            },
            {
                "name": "Seasonal Tomatoes",
                "category": "vegetables",
                "subcategory": "seasonal",
                "price": 95.00,
                "image": img("photo-1592924357228-91a4daadcfea"),
                "unit": "1 kg",
                "stock": 70,
                "description": "Vine-ripened seasonal tomatoes.",
            },
            {
                "name": "Farm Fresh Milk",
                "category": "farm-produce",
                "subcategory": "dairy",
                "price": 110.00,
                "image": img("photo-1550583724-b2692b85b150"),
                "unit": "1 L",
                "stock": 50,
                "description": "Pasteurized whole milk from local dairies.",
            },
            {
                "name": "Free-range Eggs",
                "category": "farm-produce",
                "subcategory": "eggs",
                "price": 260.00,
                "image": img("photo-1582722872445-44dc5f7e3c8f"),
                "unit": "12 pcs",
                "stock": 60,
                "description": "Free-range eggs from village hens.",
            },
            {
                "name": "Wild Honey",
                "category": "farm-produce",
                "subcategory": "honey",
                "price": 950.00,
                "image": img("photo-1587049352846-4a222e784d38"),
                "unit": "500 g",
                "stock": 30,
                "description": "Pure wild honey from the Himalayan foothills.",
            },
            {
                "name": "Pure Cow Ghee",
                "category": "farm-produce",
                "subcategory": "honey",
                "price": 1350.00,
                "image": img("photo-1631452180519-c014fe946bc7"),
                "unit": "500 g",
                "stock": 25,
                "description": "Traditional bilona cow ghee.",
            },
        ]

        products_seeded = 0
        for p_data in products_data:
            cat = category_cache.get(p_data["category"])
            sub = subcategory_cache.get(p_data["subcategory"])

            if not cat or not sub:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping product '{p_data['name']}' due to missing category/subcategory."
                    )
                )
                continue

            slug = slugify(p_data["name"])

            # Create or update product
            product, created = Product.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": p_data["name"],
                    "category": cat,
                    "subcategory": sub,
                    "price": p_data["price"],
                    "market_price": p_data.get("market_price"),
                    "image": p_data["image"],
                    "unit": p_data["unit"],
                    "description": p_data["description"],
                    "stock": p_data["stock"],
                },
            )
            if created:
                products_seeded += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded {products_seeded} products."
            )
        )
