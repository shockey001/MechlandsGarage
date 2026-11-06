"""
One-time migration: move content from content.py into the database.
Run once:
    python migrate_content.py
Safe to run multiple times — it skips items whose slug/SKU already exists.
"""

from models import (
    init_db,
    create_blog_post, create_event, create_gallery_item, create_product,
    list_blog_posts, list_events, list_gallery_items, list_products,
)
from content import BLOG_POSTS, EVENTS, GALLERY_ITEMS, SHOP_PRODUCTS


def main():
    init_db()

    # --- Blog posts ---
    existing_blog_slugs = {p['slug'] for p in list_blog_posts()}
    blog_added = 0
    for post in BLOG_POSTS:
        if post['slug'] in existing_blog_slugs:
            continue
        result = create_blog_post(
            slug=post['slug'],
            title=post['title'],
            date=post['date'],
            excerpt=post['excerpt'],
            body=post['body'],
        )
        if result:
            blog_added += 1
    print(f"Blog posts migrated: {blog_added}")

    # --- Events ---
    existing_event_slugs = {e['slug'] for e in list_events()}
    events_added = 0
    for event in EVENTS:
        if event['slug'] in existing_event_slugs:
            continue
        result = create_event(
            slug=event['slug'],
            title=event['title'],
            date=event['date'],
            location=event['location'],
            status=event['status'],
            description=event['description'],
        )
        if result:
            events_added += 1
    print(f"Events migrated: {events_added}")

    # --- Gallery items ---
    existing_gallery = {(g['image'], g['caption']) for g in list_gallery_items()}
    gallery_added = 0
    for item in GALLERY_ITEMS:
        key = (item['image'], item['caption'])
        if key in existing_gallery:
            continue
        create_gallery_item(
            image=item['image'],
            caption=item['caption'],
            category=item['category'],
        )
        gallery_added += 1
    print(f"Gallery items migrated: {gallery_added}")

    # --- Products ---
    existing_skus = {p['sku'] for p in list_products()}
    products_added = 0
    for product in SHOP_PRODUCTS:
        if product['id'] in existing_skus:
            continue
        create_product(
            sku=product['id'],
            category=product['category'],
            name=product['name'],
            description=product['description'],
            price=product['price'],
        )
        products_added += 1
    print(f"Products migrated: {products_added}")

    print("\n✅ Migration complete.")


if __name__ == "__main__":
    main()