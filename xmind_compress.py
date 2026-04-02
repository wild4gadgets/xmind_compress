#!/opt/homebrew/bin/python3
"""
xmind_compress.py — Reduce screenshot sizes in XMind files.

Usage:
    xmind_compress.py notes.xmind
    xmind_compress.py *.xmind
    xmind_compress.py file1.xmind file2.xmind --quality 85 --max-dim 1920
    xmind_compress.py notes.xmind --output notes-small.xmind
    xmind_compress.py notes.xmind --in-place
"""

import argparse
import glob
import os
import sys
import tempfile
import zipfile

try:
    from PIL import Image
except ImportError:
    sys.exit("Error: Pillow is required. Install with: pip3 install Pillow")

DEFAULT_MAX_DIM = 1440
DEFAULT_QUALITY = 80


def compress_xmind(input_path, output_path, max_dim, quality, verbose):
    """Compress images in a single XMind file. Returns (image_count, bytes_before, bytes_after)."""
    count = 0
    bytes_before = 0
    bytes_after = 0

    with tempfile.TemporaryDirectory() as tmpdir:
        # Extract the XMind ZIP
        with zipfile.ZipFile(input_path, "r") as zf:
            zf.extractall(tmpdir)

        resources_dir = os.path.join(tmpdir, "resources")
        if os.path.isdir(resources_dir):
            for filename in sorted(os.listdir(resources_dir)):
                ext = os.path.splitext(filename)[1].lower()
                if ext not in (".jpeg", ".jpg", ".png"):
                    continue

                img_path = os.path.join(resources_dir, filename)
                orig_size = os.path.getsize(img_path)
                bytes_before += orig_size

                img = Image.open(img_path)

                # Resize if larger than max_dim on either axis
                if img.width > max_dim or img.height > max_dim:
                    ratio = min(max_dim / img.width, max_dim / img.height)
                    img = img.resize(
                        (int(img.width * ratio), int(img.height * ratio)),
                        Image.LANCZOS,
                    )

                # Save compressed
                if ext in (".jpeg", ".jpg"):
                    if img.mode not in ("RGB", "L"):
                        img = img.convert("RGB")
                    img.save(img_path, "JPEG", quality=quality, optimize=True)
                else:
                    img.save(img_path, "PNG", optimize=True)

                new_size = os.path.getsize(img_path)
                bytes_after += new_size
                count += 1

                if verbose:
                    pct = (1 - new_size / orig_size) * 100 if orig_size else 0
                    print(
                        f"  {filename[:50]:<52} "
                        f"{orig_size // 1024:>6} KB -> {new_size // 1024:>5} KB  "
                        f"({pct:.0f}% smaller)"
                    )
        elif verbose:
            print("  No resources/ directory found — nothing to compress.")

        # Repackage as a new XMind (ZIP) file
        tmp_output = output_path + ".tmp"
        with zipfile.ZipFile(tmp_output, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _dirs, files in os.walk(tmpdir):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    arcname = os.path.relpath(fpath, tmpdir)
                    zf.write(fpath, arcname)

    # Atomic replace
    os.replace(tmp_output, output_path)
    return count, bytes_before, bytes_after


def output_path_for(input_path, suffix):
    """Return a default output path by inserting a suffix before the extension."""
    base, ext = os.path.splitext(input_path)
    return base + suffix + ext


def fmt_mb(n):
    return f"{n / 1024 / 1024:.1f} MB"


def main():
    parser = argparse.ArgumentParser(
        description="Compress screenshots inside XMind files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="XMind file(s) to compress. Wildcards are supported (e.g. *.xmind).",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Output file path (only valid when a single input file is given).",
    )
    parser.add_argument(
        "--in-place", "-i",
        action="store_true",
        help="Overwrite the original file instead of creating a new one.",
    )
    parser.add_argument(
        "--suffix", "-s",
        default="-compressed",
        metavar="SUFFIX",
        help='Suffix added to output filenames (default: "-compressed").',
    )
    parser.add_argument(
        "--quality", "-q",
        type=int,
        default=DEFAULT_QUALITY,
        metavar="1-95",
        help=f"JPEG quality (default: {DEFAULT_QUALITY}).",
    )
    parser.add_argument(
        "--max-dim", "-d",
        type=int,
        default=DEFAULT_MAX_DIM,
        metavar="PIXELS",
        help=f"Maximum image dimension in pixels (default: {DEFAULT_MAX_DIM}).",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print details for each image.",
    )

    args = parser.parse_args()

    # Expand any glob patterns (handles quoted wildcards like "*.xmind")
    input_files = []
    for pattern in args.files:
        expanded = glob.glob(pattern)
        if expanded:
            input_files.extend(expanded)
        else:
            # Treat as a literal path so we report the error clearly
            input_files.append(pattern)

    # Deduplicate while preserving order
    seen = set()
    input_files = [f for f in input_files if not (f in seen or seen.add(f))]

    if args.output and len(input_files) != 1:
        parser.error("--output can only be used with a single input file.")

    if args.in_place and args.output:
        parser.error("--in-place and --output are mutually exclusive.")

    total_before = 0
    total_after = 0
    success = 0
    errors = 0

    for input_path in input_files:
        if not os.path.isfile(input_path):
            print(f"Error: file not found: {input_path}", file=sys.stderr)
            errors += 1
            continue
        if not zipfile.is_zipfile(input_path):
            print(f"Error: not a valid XMind/ZIP file: {input_path}", file=sys.stderr)
            errors += 1
            continue

        # Determine output path
        if args.in_place:
            out_path = input_path
        elif args.output:
            out_path = args.output
        else:
            out_path = output_path_for(input_path, args.suffix)

        print(f"{input_path} -> {out_path}")

        try:
            count, before, after = compress_xmind(
                input_path, out_path, args.max_dim, args.quality, args.verbose
            )
        except Exception as exc:
            print(f"  Error processing file: {exc}", file=sys.stderr)
            errors += 1
            continue

        total_before += before
        total_after += after
        success += 1

        reduction = (1 - after / before) * 100 if before else 0
        print(
            f"  {count} image(s) compressed: "
            f"{fmt_mb(before)} -> {fmt_mb(after)} ({reduction:.0f}% smaller)"
        )

    # Summary when processing multiple files
    if len(input_files) > 1:
        overall = (1 - total_after / total_before) * 100 if total_before else 0
        print(
            f"\nDone: {success} file(s) compressed"
            + (f", {errors} error(s)" if errors else "")
            + f". Total: {fmt_mb(total_before)} -> {fmt_mb(total_after)} ({overall:.0f}% smaller)"
        )

    sys.exit(1 if errors and not success else 0)


if __name__ == "__main__":
    main()
