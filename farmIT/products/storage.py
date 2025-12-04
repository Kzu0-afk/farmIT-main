import logging
import mimetypes
import os
from typing import Optional
from uuid import uuid4

try:
    # supabase-py client (installed via "supabase" package)
    from supabase import Client, create_client  # type: ignore
except Exception:  # pragma: no cover - optional dependency guard
    Client = None  # type: ignore
    create_client = None  # type: ignore

logger = logging.getLogger(__name__)


def _get_supabase_client() -> Optional["Client"]:
    """
    Return a Supabase client if credentials are configured, otherwise None.

    This keeps local dev simple: if SUPABASE_URL / SUPABASE_ANON_KEY are not
    present, the caller can gracefully skip uploads and continue using plain URLs.
    """

    if create_client is None:
        logger.warning("Supabase client library is not installed; skipping uploads.")
        return None

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    if not url or not key:
        logger.info("SUPABASE_URL or SUPABASE_ANON_KEY not set; skipping uploads.")
        return None

    try:
        return create_client(url, key)
    except Exception:
        logger.exception("Failed to initialize Supabase client.")
        return None


def upload_product_image(file_obj) -> Optional[str]:
    """
    Upload a product image to Supabase Storage and return the public URL.

    - Uses bucket from SUPABASE_STORAGE_BUCKET (default: "product-images").
    - Generates a unique path per file.
    - Returns None if upload cannot be performed (missing config, errors, etc.).
    """

    client = _get_supabase_client()
    if client is None:
        return None

    bucket = os.getenv("SUPABASE_STORAGE_BUCKET", "product-images")

    # Generate a reasonably unique name; keep original name for extension.
    safe_name = getattr(file_obj, "name", "upload")
    unique_key = f"products/{uuid4().hex}-{safe_name}"

    content_type, _ = mimetypes.guess_type(safe_name)
    options = {}
    if content_type:
        options["content-type"] = content_type

    try:
        # Read the file bytes; reset pointer afterwards for any further use.
        data = file_obj.read()
        file_obj.seek(0)

        # Upload to Supabase Storage.
        client.storage.from_(bucket).upload(
            unique_key,
            data,
            file_options=options or None,
        )

        public_url = client.storage.from_(bucket).get_public_url(unique_key)
        return public_url
    except Exception:
        logger.exception("Failed to upload product image to Supabase Storage.")
        return None


