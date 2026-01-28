#!/usr/bin/env python3
"""
Naloži izbrane .html datoteke na podpisno tablico prek HTTP kot /assets/{ime}.html

Uporaba:
 - Skripto zaženi v isti mapi kot .html datoteke
 - Izberi eno/več/vse datoteke iz prikazane liste
 - Vsaka izbrana datoteka se naloži na: http://{IP}:12345/assets/{ime_datoteke}
"""

import os
import requests

TABLICA_IP = "10.0.110.130"
TABLICA_URL = f"http://{TABLICA_IP}:12345"


def find_html_files(directory):
    return [f for f in os.listdir(directory) if f.lower().endswith('.html') and os.path.isfile(os.path.join(directory, f))]


def print_numbered(files):
    for idx, name in enumerate(files, start=1):
        print(f"{idx}. {name}")


def parse_selection(user_input, total):
    s = user_input.strip().lower()
    if s in ("vse", "all", "a", "*"):
        return list(range(1, total + 1))
    parts = [p.strip() for p in s.replace(" ", "").split(',') if p.strip()]
    selection = []
    for p in parts:
        if '-' in p:
            start_str, end_str = p.split('-', 1)
            start_idx = int(start_str)
            end_idx = int(end_str)
            if start_idx < 1 or end_idx > total or start_idx > end_idx:
                raise ValueError(f"Neveljaven interval: {p}")
            selection.extend(range(start_idx, end_idx + 1))
        else:
            idx = int(p)
            if idx < 1 or idx > total:
                raise ValueError(f"Neveljavna izbira: {p}")
            selection.append(idx)
    seen = set()
    unique = []
    for i in selection:
        if i not in seen:
            seen.add(i)
            unique.append(i)
    return unique


def upload_html_file(file_path, base_url):
    file_name = os.path.basename(file_path)
    dest_url = f"{base_url}/assets/{file_name}"
    print(f"\nNalagam {file_name} -> /assets/{file_name} ...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        response = requests.post(
            dest_url,
            data=html_content.encode('utf-8'),
            headers={"Content-Type": "text/html; charset=utf-8"},
            timeout=15
        )
        if 200 <= response.status_code < 300:
            try:
                result = response.json()
                size_info = result.get('size')
                if size_info is not None:
                    print(f"   OK USPEŠNO! Velikost: {size_info:,} bytov")
                else:
                    print("   OK USPEŠNO!")
            except Exception:
                print("   OK USPEŠNO!")
            return True
        else:
            print(f"   NAPAKA: Status {response.status_code}")
            return False
    except FileNotFoundError:
        print("   NAPAKA: Datoteka ne obstaja!")
        return False
    except Exception as e:
        print(f"   NAPAKA: {e}")
        return False


def main():
    print("=" * 70)
    print("Nalaganje .html datotek na podpisno tablico")
    print("=" * 70)

    cwd = os.path.abspath(os.path.dirname(__file__))
    html_files = find_html_files(cwd)

    if not html_files:
        print("V trenutni mapi ni .html datotek.")
        exit(1)

    print("\nNajdene .html datoteke:")
    print_numbered(html_files)
    print("\nIzberi (npr. 1,3,5 ali 2-4) ali vpiši 'vse':")
    selection_raw = input("> ")

    try:
        indices = parse_selection(selection_raw, len(html_files))
    except Exception as e:
        print(str(e))
        exit(1)

    selected = [os.path.join(cwd, html_files[i - 1]) for i in indices]

    successes = 0
    for path in selected:
        if upload_html_file(path, TABLICA_URL):
            successes += 1

    print("\n" + "=" * 70)
    print(f"NALAGANJE KONČANO! Uspešno: {successes}/{len(selected)}")
    print("=" * 70)
    if successes:
        print("\nNASLEDNJI KORAKI:")
        print()
        print("1. Po potrebi restart aplikacije na tablici")
        print("2. Odpri /assets/{ime_datoteke} za preverjanje pravilnosti nalaganja")


if __name__ == "__main__":
    main()