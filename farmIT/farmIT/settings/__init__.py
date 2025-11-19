import os

# Simple dynamic environment selector.
# Leave DJANGO_SETTINGS_MODULE as "farmIT.settings" everywhere,
# and switch by setting DJANGO_ENV to "prod" or "dev" (default dev).
env = os.getenv("DJANGO_ENV", "dev").strip().lower()
if env.startswith("prod"):
    from .prod import *  # type: ignore  # noqa: F401,F403
else:
    from .dev import *  # type: ignore  # noqa: F401,F403

