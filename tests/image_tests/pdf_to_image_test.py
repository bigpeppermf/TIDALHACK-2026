from app.utils.pdf import pdf_to_images

images = pdf_to_images("test_notes.pdf", max_pages=5)

print(f"Extracted {len(images)} pages")

for i, img in enumerate(images):
    img.save(f"page_{i+1}.png")
    print(f"Saved page_{i+1}.png")
