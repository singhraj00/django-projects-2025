import pandas as pd
import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from apps.tours.models import Tour, TourImage


class Command(BaseCommand):
    help = "Import tours from CSV file"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to CSV file")

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]

        self.stdout.write(self.style.SUCCESS(f"Reading CSV: {file_path}"))

        df = pd.read_csv(file_path).fillna("")

        for index, row in df.iterrows():
            title = row.get('title', '').strip()

            if not title:
                self.stdout.write(self.style.ERROR(f"Row {index+1} skipped: Missing title"))
                continue

            if Tour.objects.filter(title=title).exists():
                self.stdout.write(self.style.WARNING(f"Tour '{title}' already exists. Skipped."))
                continue

            # Create tour
            tour = Tour.objects.create(
                title=title,
                location=row.get('location', ''),
                price=row.get('price', 0),
                duration=row.get('duration', ''),
                description=row.get('description', ''),
                image_url=row.get('main_image_url', '')
            )

            # Main image
            main_url = row.get('main_image_url', '').strip()
            if main_url:
                try:
                    resp = requests.get(main_url, timeout=10)
                    resp.raise_for_status()
                    tour.image.save(
                        f"{title.replace(' ', '_')}_main.jpg",
                        ContentFile(resp.content),
                        save=True
                    )
                    self.stdout.write(self.style.SUCCESS(f"Main image OK for: {title}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Main image failed for '{title}': {e}"))

            # Extra images
            extra = row.get('extra_images_urls', '').strip()
            if extra:
                urls = [u.strip() for u in extra.split("|") if u.strip()]
                for i, url in enumerate(urls):
                    try:
                        resp = requests.get(url, timeout=10)
                        resp.raise_for_status()
                        img = TourImage(tour=tour)
                        img.image.save(
                            f"{title.replace(' ', '_')}_extra_{i+1}.jpg",
                            ContentFile(resp.content),
                            save=True
                        )
                        self.stdout.write(self.style.SUCCESS(f"Extra image {i+1} added for {title}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Extra image {i+1} failed for {title}: {e}"))

        self.stdout.write(self.style.SUCCESS("\n🎉 All tours imported successfully!"))
