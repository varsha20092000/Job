# fix_encoding.py
input_file = 'admin_jobs.json'
output_file = 'admin_jobs_fixed.json'



with open(input_file, "rb") as f:
    raw_data = f.read()

# decode using ISO-8859-1 or latin-1 (can handle 0x96)
text = raw_data.decode("latin-1")

# save as proper utf-8
with open(output_file, "w", encoding="utf-8") as f:
    f.write(text)

print("✅ File cleaned and saved as:", output_file)
