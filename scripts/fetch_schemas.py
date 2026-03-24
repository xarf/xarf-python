#!/usr/bin/env python3
"""Fetch XARF schemas from the official xarf-spec GitHub release.

This script downloads JSON schemas from a specific tagged release of
https://github.com/xarf/xarf-spec and extracts them into xarf/schemas/.

The target spec version is read from ``[tool.xarf] spec_version`` in
``pyproject.toml``. Run this script before publishing a new library release
to update the bundled schemas.

Usage:
    python scripts/fetch_schemas.py
    python scripts/fetch_schemas.py --force   # re-fetch even if up to date
"""

import argparse
import datetime
import io
import json
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

GITHUB_REPO = "xarf/xarf-spec"
REPO_ROOT = Path(__file__).parent.parent
SCHEMAS_DIR = REPO_ROOT / "xarf" / "schemas"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"


def get_configured_version() -> str:
    """Read the target spec version from pyproject.toml.

    Returns:
        The spec version string (e.g. ``"v4.2.0"``).

    Raises:
        SystemExit: If the version key is missing or pyproject.toml is unreadable.
    """
    # tomllib is stdlib in 3.11+; tomli is the backport for 3.10
    try:
        import tomllib  # noqa: PLC0415
    except ImportError:
        try:
            import tomli as tomllib  # type: ignore[no-redef]  # noqa: PLC0415
        except ImportError:
            print(
                "ERROR: tomllib not available. Use Python 3.11+ or install tomli.",
                file=sys.stderr,
            )
            sys.exit(1)

    try:
        with PYPROJECT_PATH.open("rb") as f:
            data = tomllib.load(f)
    except OSError as exc:
        print(f"ERROR: Cannot read {PYPROJECT_PATH}: {exc}", file=sys.stderr)
        sys.exit(1)

    version = data.get("tool", {}).get("xarf", {}).get("spec_version")
    if not version:
        print(
            "ERROR: [tool.xarf] spec_version not found in pyproject.toml.",
            file=sys.stderr,
        )
        sys.exit(1)

    return version


def needs_fetch(version: str) -> bool:
    """Check whether schemas need to be (re-)fetched.

    Args:
        version: Target spec version string.

    Returns:
        ``True`` if the local schemas are absent or pinned to a different version.
    """
    version_file = SCHEMAS_DIR / ".version"
    if not version_file.exists():
        return True
    try:
        info = json.loads(version_file.read_text())
        return info.get("version") != version
    except (json.JSONDecodeError, OSError):
        return True


def download(url: str) -> bytes:
    """Download a URL, following redirects, with a 60-second timeout.

    Args:
        url: The URL to download.

    Returns:
        The raw response bytes.

    Raises:
        SystemExit: On HTTP error or timeout.
    """
    print(f"[xarf] Downloading {url}...")
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "xarf-python/fetch-schemas"}
        )
        with urllib.request.urlopen(req, timeout=60) as response:
            data = response.read()
        print(f"[xarf] Downloaded {len(data) / 1024:.1f} KB")
        return data
    except urllib.error.HTTPError as exc:
        print(f"ERROR: HTTP {exc.code} fetching {url}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


def extract_and_copy(tarball: bytes, version: str) -> None:
    """Extract schemas/v4/ from the tarball into xarf/schemas/.

    Args:
        tarball: Raw ``.tar.gz`` bytes.
        version: Version string, used to locate the extracted root directory.

    Raises:
        SystemExit: If the expected directory structure is not found in the tarball.
    """
    print("[xarf] Extracting schemas...")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with tarfile.open(fileobj=io.BytesIO(tarball), mode="r:gz") as tf:
            tf.extractall(tmp_path)  # noqa: S202  (trusted GitHub tarball)

        # GitHub tarballs extract to xarf-spec-{version-without-v}/
        version_without_v = version.lstrip("v")
        candidate = tmp_path / f"xarf-spec-{version_without_v}"
        if not candidate.is_dir():
            # Fall back: find the first directory in the temp root
            dirs = [p for p in tmp_path.iterdir() if p.is_dir()]
            if not dirs:
                print("ERROR: No directory found in tarball.", file=sys.stderr)
                sys.exit(1)
            candidate = dirs[0]

        source = candidate / "schemas" / "v4"
        if not source.is_dir():
            print(
                f"ERROR: schemas/v4/ not found inside tarball at {source}",
                file=sys.stderr,
            )
            sys.exit(1)

        # Replace xarf/schemas/ with fresh content
        if SCHEMAS_DIR.exists():
            shutil.rmtree(SCHEMAS_DIR)
        SCHEMAS_DIR.mkdir(parents=True)
        (SCHEMAS_DIR / "types").mkdir()

        for item in source.iterdir():
            if item.is_file() and item.suffix == ".json":
                shutil.copy2(item, SCHEMAS_DIR / item.name)
                print(f"[xarf]   - {item.name}")

        types_src = source / "types"
        if types_src.is_dir():
            for item in types_src.iterdir():
                if item.is_file() and item.suffix == ".json":
                    shutil.copy2(item, SCHEMAS_DIR / "types" / item.name)
                    print(f"[xarf]   - types/{item.name}")


def write_version_info(version: str) -> None:
    """Write a .version file recording the fetched spec version.

    Args:
        version: The spec version string that was fetched.
    """
    info = {
        "version": version,
        "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source": f"https://github.com/{GITHUB_REPO}/tree/{version}",
    }
    (SCHEMAS_DIR / ".version").write_text(json.dumps(info, indent=2) + "\n")


def fetch_schemas(force: bool = False) -> None:
    """Main entry point: fetch and install schemas from GitHub.

    Args:
        force: If ``True``, fetch even when the local version is already current.
    """
    version = get_configured_version()
    print(f"[xarf] Checking schemas for xarf-spec {version}...")

    if not force and not needs_fetch(version):
        print(f"[xarf] Schemas already up to date ({version})")
        return

    tarball_url = f"https://github.com/{GITHUB_REPO}/archive/refs/tags/{version}.tar.gz"
    tarball = download(tarball_url)
    extract_and_copy(tarball, version)
    write_version_info(version)
    print(f"[xarf] Successfully fetched schemas for xarf-spec {version}")


def main() -> None:
    """Parse CLI arguments and run the fetch."""
    parser = argparse.ArgumentParser(
        description="Fetch XARF JSON schemas from the xarf-spec GitHub release."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-fetch even if the local schemas are already at the target version.",
    )
    args = parser.parse_args()
    fetch_schemas(force=args.force)


if __name__ == "__main__":
    main()
