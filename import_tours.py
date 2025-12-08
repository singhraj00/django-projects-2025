import pandas as pd
import requests
from django.core.files.base import ContentFile
from apps.tours.models import Tour, TourImage  # replace myapp with your app name

# CSV path
file_path = 'travelapp_docs.csv' 
df = pd.read_csv(file_path)

for index, row in df.iterrows():
    # 1️⃣ Create Tour
    tour = Tour.objects.create(
        title=row['title'],
        location=row['location'],
        price=row['price'],
        duration=row['duration'],
        description=row['description'],
        image_url=row.get('main_image_url')
    )

    # 2️⃣ Download main image (optional: save locally)
    if row.get('main_image_url'):
        try:
            resp = requests.get(row['main_image_url'])
            if resp.status_code == 200:
                tour.image.save(
                    f"{row['title'].replace(' ', '_')}_main.jpg",
                    ContentFile(resp.content),
                    save=True
                )
        except Exception as e:
            print(f"Failed to download main image for {row['title']}: {e}")

    # 3️⃣ Extra images
    extra_images = row.get('extra_images_urls')
    if pd.notna(extra_images):
        urls = [url.strip() for url in extra_images.split(',')]
        for i, url in enumerate(urls):
            try:
                resp = requests.get(url)
                if resp.status_code == 200:
                    img = TourImage(tour=tour)
                    img.image.save(
                        f"{row['title'].replace(' ', '_')}_extra{i+1}.jpg",
                        ContentFile(resp.content),
                        save=True
                    )
            except Exception as e:
                print(f"Failed to download extra image {i+1} for {row['title']}: {e}")

print("All tours imported successfully!")
