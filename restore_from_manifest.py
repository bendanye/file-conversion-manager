from pathlib import Path
import shutil
import sys


def parse_manifest(manifest_file: Path):
    """
    Parse the manifest and return a list of
    (original_file, output_file) tuples.
    """

    entries = []

    current_original = None
    current_output = None

    with manifest_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            # Ignore manifest header
            if line.startswith("File Copy Manifest"):
                continue

            if line.startswith("=================="):
                continue

            if line.startswith("Original:"):
                current_original = line[len("Original:"):].strip()

            elif line.startswith("Output:"):
                current_output = line[len("Output:"):].strip()

            # Once we have both values, create an entry
            if current_original and current_output:
                entries.append(
                    (
                        Path(current_original),
                        Path(current_output),
                    )
                )

                current_original = None
                current_output = None

    return entries


def restore_files(manifest_file: Path, overwrite: bool = False):
    """
    Restore all files listed in the manifest.
    """

    if not manifest_file.exists():
        raise FileNotFoundError(
            f"Manifest does not exist: {manifest_file}"
        )

    if not manifest_file.is_file():
        raise ValueError(
            f"Manifest is not a file: {manifest_file}"
        )

    entries = parse_manifest(manifest_file)

    if not entries:
        print("No files found in manifest.")
        return

    restored = 0
    skipped = 0
    failed = 0

    print(f"Found {len(entries)} file(s) in manifest.")
    print()

    for original_file, output_file in entries:

        try:
            # Check that the source file exists
            if not output_file.exists():
                print(
                    f"[SKIP] Source file does not exist:\n"
                    f"       {output_file}"
                )

                skipped += 1
                continue

            if not output_file.is_file():
                print(
                    f"[SKIP] Source is not a file:\n"
                    f"       {output_file}"
                )

                skipped += 1
                continue

            # Check whether the destination already exists
            if original_file.exists():

                if not overwrite:
                    print(
                        f"[SKIP] Destination already exists:\n"
                        f"       {original_file}"
                    )

                    skipped += 1
                    continue

                print(
                    f"[OVERWRITE] {original_file}"
                )

            # Create parent directory
            original_file.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            # Copy the file back
            shutil.copy2(
                output_file,
                original_file
            )

            print(
                f"[RESTORED]\n"
                f"  From: {output_file}\n"
                f"  To:   {original_file}\n"
            )

            restored += 1

        except Exception as e:
            print(
                f"[ERROR]\n"
                f"  Source: {output_file}\n"
                f"  Target: {original_file}\n"
                f"  Error:  {e}\n"
            )

            failed += 1

    print()
    print("================================")
    print("Restore Summary")
    print("================================")
    print(f"Total:    {len(entries)}")
    print(f"Restored: {restored}")
    print(f"Skipped:  {skipped}")
    print(f"Failed:   {failed}")


def main():
    manifest_file = Path("./output/manifest.txt").resolve()

    try:
        restore_files(
            manifest_file,
            overwrite=True
        )

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
