"""Non-production (NPD) application package.

Re-exports the console entry point and the application factory declared in
``npd.main``.
"""

from npd.main import main, build_application
