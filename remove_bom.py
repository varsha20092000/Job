# remove_bom.py
input_file = "jobs_from_sqlite_clean.json"
output_file = "jobs_fixed.json"

with open(input_file, "r", encoding="utf-8-sig") as f:
    content = f.read()

with open(output_file, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ BOM removed and saved as:", output_file)
