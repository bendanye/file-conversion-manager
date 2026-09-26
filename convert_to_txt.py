from pathlib import Path
import shutil


def generate_output_filename(output_dir: Path, original_file: Path) -> Path:
    """
    Generate an output filename using the original filename with
    its extension changed to .txt.

    If the filename already exists, append _1, _2, etc.
    """

    base_name = original_file.stem
    output_file = output_dir / f"{base_name}.txt"

    counter = 1

    while output_file.exists():
        output_file = output_dir / f"{base_name}_{counter}.txt"
        counter += 1

    return output_file


def process_directory(input_dir: Path, output_dir: Path):
    """
    Recursively find all files under input_dir, copy them to output_dir
    with a .txt extension, and generate a manifest.
    """

    if not input_dir.exists():
        raise FileNotFoundError(
            f"Input directory does not exist: {input_dir}"
        )

    if not input_dir.is_dir():
        raise NotADirectoryError(
            f"Input path is not a directory: {input_dir}"
        )

    # Create output directory if it does not exist
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_entries = []

    # Recursively iterate through all files
    for source_file in input_dir.rglob("*"):

        # Skip directories
        if not source_file.is_file():
            continue

        # Don't accidentally process files inside the output directory
        if output_dir.resolve() in source_file.resolve().parents:
            continue

        # Generate output filename
        output_file = generate_output_filename(
            output_dir,
            source_file
        )

        # Copy the file
        shutil.copy2(source_file, output_file)

        # Record information for the manifest
        manifest_entries.append(
            f"Original: {source_file.resolve()}\n"
            f"Output:   {output_file.resolve()}\n"
        )

        print(f"Copied: {source_file} -> {output_file}")

    # Generate manifest after all files have been processed
    manifest_file = output_dir / "manifest.txt"

    with manifest_file.open("w", encoding="utf-8") as f:
        f.write("File Copy Manifest\n")
        f.write("==================\n\n")

        for entry in manifest_entries:
            f.write(entry)
            f.write("\n")

    print()
    print(f"Processed {len(manifest_entries)} file(s)")
    print(f"Manifest: {manifest_file}")


def main():
    input_dir = Path("/Users/benjaminng/Downloads/ansible-loop-engineering").resolve()
    output_dir = Path("./output").resolve()

    process_directory(input_dir, output_dir)


if __name__ == "__main__":
    main()

