# remove_bom.py
input_file = "full_jobs_clean.json"
output_file = "cleaned_jobs.json"

with open(input_file, "r", encoding="latin1") as f:
    content = f.read()

# Save as UTF-8 (without BOM)
with open(output_file, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ BOM removed and saved as:", output_file)
