"""
Downloader and Preprocessor for the Cornell Movie-Dialogs Corpus.
Fetches the official corpus archive, extracts movie lines and character metadata,
and formats dialogues into 'Speaker: Line' format for the Comic Dialogue Pipeline.
"""

import os
import sys
import zipfile
import requests
import urllib3
from typing import Dict, List, Tuple

urllib3.disable_warnings()

CORNELL_ZIP_URL = "https://www.cs.cornell.edu/~cristian/data/cornell_movie_dialogs_corpus.zip"
TARGET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
ZIP_PATH = os.path.join(TARGET_DIR, "cornell_movie_dialogs_corpus.zip")
EXTRACT_DIR = os.path.join(TARGET_DIR, "cornell_movie_dialogs_corpus")


def download_corpus(url: str = CORNELL_ZIP_URL, dest_path: str = ZIP_PATH) -> str:
    """
    Downloads the Cornell Movie-Dialogs Corpus zip file with download progress.
    """
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 9000000:
        print(f"[+] Zip archive already exists and is valid ({os.path.getsize(dest_path):,} bytes) at: {dest_path}")
        return dest_path

    print(f"[+] Downloading Cornell Movie-Dialogs Corpus from:\n    {url}")
    print(f"[+] Destination: {dest_path}")

    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, stream=True, verify=False, headers=headers, timeout=60)
    resp.raise_for_status()

    total_size = int(resp.headers.get("content-length", 0))
    downloaded = 0
    chunk_size = 128 * 1024

    with open(dest_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    mb_down = downloaded / (1024 * 1024)
                    mb_tot = total_size / (1024 * 1024)
                    sys.stdout.write(f"\r    Progress: {percent:5.1f}% ({mb_down:5.1f}MB / {mb_tot:5.1f}MB)")
                    sys.stdout.flush()

    print(f"\n[+] Download complete! File size: {os.path.getsize(dest_path):,} bytes")
    return dest_path


def extract_corpus(zip_path: str = ZIP_PATH, extract_to: str = EXTRACT_DIR) -> str:
    """
    Extracts the zip file contents.
    """
    print(f"[+] Extracting archive to: {extract_to}")
    os.makedirs(extract_to, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_to)
    print("[+] Extraction complete!")
    return extract_to


def locate_file(folder: str, filename: str) -> str:
    """
    Finds a file inside folder or its subdirectories.
    """
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower() == filename.lower():
                return os.path.join(root, f)
    raise FileNotFoundError(f"Could not find {filename} in {folder}")


def parse_and_export_dialogues(extract_dir: str = EXTRACT_DIR):
    """
    Parses 'movie_lines.txt' and 'movie_titles_metadata.txt' into
    'SPEAKER: dialogue' formatted dataset files.
    """
    lines_file = locate_file(extract_dir, "movie_lines.txt")
    titles_file = locate_file(extract_dir, "movie_titles_metadata.txt")
    
    # 1. Parse movie titles
    movies: Dict[str, str] = {}
    with open(titles_file, "r", encoding="iso-8859-1") as f:
        for line in f:
            parts = [p.strip() for p in line.split("+++$+++")]
            if len(parts) >= 2:
                movie_id = parts[0]
                movie_title = parts[1]
                movies[movie_id] = movie_title

    print(f"[+] Indexed {len(movies)} movie titles from metadata.")

    # 2. Parse lines
    # Format: lineID +++$+++ characterID +++$+++ movieID +++$+++ characterName +++$+++ text
    all_dialogue_lines: List[str] = []
    comic_superhero_dialogue: List[str] = []
    
    superhero_keywords = ["batman", "superman", "spider-man", "spiderman", "x-men", "blade", "hulk", "avengers", "iron man", "daredevil", "watchmen", "crow"]
    superhero_movie_ids = {
        m_id for m_id, title in movies.items()
        if any(kw in title.lower() for kw in superhero_keywords)
    }

    matching_titles = [movies[mid] for mid in superhero_movie_ids]
    print(f"[+] Identified {len(superhero_movie_ids)} comic/superhero movie scripts: {matching_titles}")

    total_parsed = 0
    with open(lines_file, "r", encoding="iso-8859-1") as f:
        for raw in f:
            parts = [p.strip() for p in raw.split("+++$+++")]
            if len(parts) >= 5:
                char_name = parts[3]
                movie_id = parts[2]
                utterance = parts[4]
                
                if char_name and utterance:
                    formatted = f"{char_name.upper()}: {utterance}"
                    all_dialogue_lines.append(formatted)
                    if movie_id in superhero_movie_ids:
                        comic_superhero_dialogue.append(formatted)
                    total_parsed += 1

    print(f"[+] Total dialogue lines parsed: {total_parsed:,}")

    # 3. Export curated datasets
    # Dataset A: Sample 1000 lines
    sample_path = os.path.join(TARGET_DIR, "cornell_sample_1000.txt")
    with open(sample_path, "w", encoding="utf-8") as f:
        f.write("# Cornell Movie-Dialogs Corpus: 1000-Line Benchmark Sample\n")
        f.write("# Format: SPEAKER: dialogue\n")
        for line in all_dialogue_lines[:1000]:
            f.write(line + "\n")
    print(f"[+] Exported 1,000-line sample dataset to: {sample_path}")

    # Dataset B: Superhero / Comic Movies dialogues
    if comic_superhero_dialogue:
        comic_path = os.path.join(TARGET_DIR, "cornell_superhero_dialogue.txt")
        with open(comic_path, "w", encoding="utf-8") as f:
            f.write("# Cornell Movie-Dialogs Corpus: Superhero & Comic Script Dialogue\n")
            f.write("# Format: SPEAKER: dialogue\n")
            for line in comic_superhero_dialogue:
                f.write(line + "\n")
        print(f"[+] Exported {len(comic_superhero_dialogue):,} comic/superhero dialogue lines to: {comic_path}")

    # Dataset C: Sample 5000 lines for medium scale test
    sample_5000_path = os.path.join(TARGET_DIR, "cornell_sample_5000.txt")
    with open(sample_5000_path, "w", encoding="utf-8") as f:
        f.write("# Cornell Movie-Dialogs Corpus: 5000-Line Benchmark Sample\n")
        f.write("# Format: SPEAKER: dialogue\n")
        for line in all_dialogue_lines[:5000]:
            f.write(line + "\n")
    print(f"[+] Exported 5,000-line sample dataset to: {sample_5000_path}")


def main():
    print("=" * 70)
    print("      CORNELL MOVIE-DIALOGS DATASET INSTALLER & FORMATTER")
    print("=" * 70)
    zip_p = download_corpus()
    ext_dir = extract_corpus(zip_p)
    parse_and_export_dialogues(ext_dir)
    print("=" * 70)
    print("[SUCCESS] Cornell Movie-Dialogs dataset installed and ready for analysis!")


if __name__ == "__main__":
    main()
