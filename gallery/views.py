import cloudinary
from cloudinary import Search
from django.shortcuts import render

def gallery_view(request):
    artworks = []
    try:
        response = (
            Search()
            .expression("folder:gallery/*")
            .sort_by("public_id", "desc")
            .max_results(50)
            .with_field("metadata")
            .execute()
        )

        for res in response.get("resources", []):
            url = res.get("secure_url")
            metadata = res.get("metadata", {})

            title = metadata.get("tittle") or "Untitled"
            price = metadata.get("price") or "N/A"

            artworks.append({
                "url": url,
                "title": title,
                "price": price
            })

    except Exception as e:
        print("Cloudinary error:", e)

    return render(request, "gallery.html", {"artworks": artworks})
