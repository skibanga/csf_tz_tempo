import frappe
from frappe import _
import mimetypes


def optimize_images(images_size=None):
    # Functhion to run optimize images for all images in the site
    filters = {}
    if images_size:
        filters["file_size"] = ["<=", images_size]
    images = frappe.get_all(
        "File",
        filters=filters,
        or_filters=[
            {"file_url": ["like", "%.png"]},
            {"file_url": ["like", "%.jpg"]},
            {"file_url": ["like", "%.jpeg"]},
            {"file_url": ["like", "%.PNG"]},
            {"file_url": ["like", "%.JPG"]},
            {"file_url": ["like", "%.JPEG"]},
        ],
        limit_page_length=10,
    )
    # Loop through all images
    for image in images:
        try:
            # Get image file
            image_file = frappe.get_doc("File", image.name)
            # validate image type
            content_type = mimetypes.guess_type(image_file.file_name)[0]
            is_local_image = (
                content_type.startswith("image/") and image_file.file_size > 0
            )
            is_svg = content_type == "image/svg+xml"
            if not is_local_image:
                continue
            if is_svg:
                continue
            # Optimize image
            image_file.optimize_file()
            # Save image
            image_file.save()
            # Commit
            frappe.db.commit()
        except Exception as e:
            # Log error
            frappe.log_error(frappe.get_traceback(), str(e))
    # Return message
    return _("Images optimized successfully")
