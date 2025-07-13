# fix_encoding.py
import json

with open("admin_jobs.json", "r", encoding="utf-8", errors="replace") as infile:
    data = json.load(infile)

with open("admin_jobs_fixed.json", "w", encoding="utf-8") as outfile:
    json.dump(data, outfile, ensure_ascii=False, indent=4)

print("✅ Fixed encoding and saved as admin_jobs_fixed.json")
