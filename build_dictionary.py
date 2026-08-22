#!/usr/bin/env python3
"""
build_dictionary.py
-------------------
Fetches the Hebrew Wiktionary titles dump and produces a clean
words-full.json suitable for embedding in word-finder.html.

Usage:
    pip install requests
    python build_dictionary.py

Output:
    words-full.json   — commit this to your crosswords repo
"""

import gzip, json, re, sys, os
import urllib.request
from pathlib import Path

DUMP_URL  = "https://dumps.wikimedia.org/hewiktionary/latest/hewiktionary-latest-all-titles-in-ns0.gz"
DUMP_FILE = "hewiktionary-titles.gz"
OUT_FILE  = "words-full.json"

# Only characters in the Hebrew Unicode block (U+05D0–U+05EA), optional
# vowel points (nikud U+05B0–U+05BD, U+05BF, U+05C1–U+05C2, U+05C4–U+05C7)
# and geresh/gershayim (U+05F3–U+05F4) for words like ג׳ירפה.
# We strip nikud from the stored form so matching is nikud-agnostic.
HEBREW_LETTER = re.compile(r'^[\u05D0-\u05EA\u05B0-\u05BD\u05BF\u05C1\u05C2\u05C4-\u05C7\u05F3\u05F4]+$')
NIKUD        = re.compile(r'[\u05B0-\u05BD\u05BF\u05C1\u05C2\u05C4-\u05C7]')
FINAL_MAP    = str.maketrans('ךםןףץ', 'כמנפצ')  # for length counting only, not stored

MIN_LEN = 2   # skip single letters
MAX_LEN = 20  # skip suspiciously long strings

def strip_nikud(w):
    return NIKUD.sub('', w)

def is_valid(w):
    if not HEBREW_LETTER.match(w):
        return False
    plain = strip_nikud(w)
    return MIN_LEN <= len(plain) <= MAX_LEN

def download_dump():
    if Path(DUMP_FILE).exists():
        size = os.path.getsize(DUMP_FILE)
        print(f"Found cached dump ({size//1024} KB), skipping download.")
        print("Delete", DUMP_FILE, "to force a fresh download.")
        return
    print("Downloading Wiktionary dump (~10-30 MB)...")
    print(DUMP_URL)
    def progress(count, block, total):
        if total > 0:
            pct = count * block * 100 // total
            print(f"\r  {pct}%", end='', flush=True)
    urllib.request.urlretrieve(DUMP_URL, DUMP_FILE, reporthook=progress)
    print(f"\nDone. {os.path.getsize(DUMP_FILE)//1024} KB saved.")

def extract_words():
    print("Reading and filtering titles...")
    words = set()
    with gzip.open(DUMP_FILE, 'rt', encoding='utf-8', errors='ignore') as f:
        for line in f:
            word = line.strip()
            # Strip nikud for the stored form
            plain = strip_nikud(word)
            if is_valid(plain):
                words.add(plain)
    return words

def main():
    download_dump()
    words = extract_words()
    print(f"Found {len(words):,} valid Hebrew words")

    # Merge with any existing dictionary.json so we don't lose hand-curated
    # preposition/pronoun forms that may not be in Wiktionary titles
    existing = set()
    if Path('dictionary.json').exists():
        d = json.load(open('dictionary.json', encoding='utf-8'))
        base = d.get('words', [])
        existing = set(base)
        print(f"Merging with existing dictionary.json ({len(existing)} words)...")
        words |= existing

    sorted_words = sorted(words)
    print(f"Total after merge: {len(sorted_words):,} words")

    out = {
        "description": (
            "Hebrew word list for the crossword word-finder tool. "
            "Sourced from Hebrew Wiktionary (https://he.wiktionary.org) titles dump "
            "under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), "
            "merged with a hand-curated preposition/particle list. "
            "Individual words are not copyrightable; the Wiktionary attribution "
            "is included as good practice."
        ),
        "wordCount": len(sorted_words),
        "source": "he.wiktionary.org titles dump + hand-curated seed",
        "words": sorted_words
    }

    json.dump(out, open(OUT_FILE, 'w', encoding='utf-8'), ensure_ascii=False)
    # Check file size
    size_kb = Path(OUT_FILE).stat().st_size // 1024
    print(f"\nWrote {OUT_FILE} ({size_kb} KB, {len(sorted_words):,} words)")

    if size_kb > 2000:
        print("\nNote: file is large (>2MB). The app loads it via fetch with")
        print("cache:no-store only on a hard-reload — normal visits use localStorage,")
        print("so users only pay the download cost once.")
    else:
        print("Size looks fine for a GitHub Pages static file.")

if __name__ == '__main__':
    main()
