# remove_bom.py
input_file = "full_data.json"
output_file = "full_data.json"  # Overwrite the same file

with open(input_file, "r", encoding="utf-8-sig") as f:
    content = f.read()

with open(output_file, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ BOM removed from full_data.json")
