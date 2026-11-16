"""
EDUGATE Admin Panel Bundler
Yordamchi skript: `template.html` va uning tarkibidagi barcha modullar
(`components/`, `views/`, `js/`, `css/`)ni yagona `index.html` faylga yig'adi.
"""

import os
import re
import sys

def bundle_admin():
    base_dir = os.path.join(os.path.dirname(__file__), "app", "static", "admin")
    template_path = os.path.join(base_dir, "template.html")
    output_path = os.path.join(base_dir, "index.html")

    if not os.path.exists(template_path):
        print(f"Xatolik: Shablon fayli topilmadi: {template_path}")
        return False

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    included_files = []

    def replacer(match):
        inc_file = match.group(1).strip()
        full_path = os.path.join(base_dir, inc_file)
        if os.path.exists(full_path):
            included_files.append(inc_file)
            with open(full_path, "r", encoding="utf-8") as inc_f:
                return inc_f.read()
        print(f"Ogohlantirish: Qo'shiladigan fayl topilmadi: {inc_file}")
        return f"<!-- missing {inc_file} -->"

    bundled = re.sub(r"<!--\s*include:\s*([^\s>]+)\s*-->", replacer, template)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(bundled)

    print("=" * 60)
    print("EDUGATE Admin Panel muvaffaqiyatli yig'ildi (bundled)!")
    print(f"Chiqish fayli: {output_path} ({len(bundled):,} bayt)")
    print(f"Birlashtirilgan fayllar soni: {len(included_files)}")
    for f in included_files:
        print(f"  + {f}")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = bundle_admin()
    sys.exit(0 if success else 1)
