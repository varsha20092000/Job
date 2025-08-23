import codecs

input_file = "full_data.json"
output_file = "full_data_clean.json"

with open(input_file, "rb") as f:
    raw = f.read()

# Decode from UTF-16 to UTF-8
text = raw.decode("utf-16")

with open(output_file, "w", encoding="utf-8") as f:
    f.write(text)

print(f"✅ Converted {input_file} from UTF-16 → UTF-8")
