import re, os

input_file = "sqlite_dump.sql"
output_dir = "split_inserts"
os.makedirs(output_dir, exist_ok=True)

with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
    sql = f.read()

# Extract only INSERT statements
inserts = re.findall(r"(INSERT INTO .*?;)", sql, flags=re.IGNORECASE | re.DOTALL)

for ins in inserts:
    # Normalize table name
    m = re.match(r'INSERT INTO "?([A-Za-z0-9_]+)"?', ins, flags=re.IGNORECASE)
    if not m: 
        continue
    table = m.group(1).lower()

    # Clean line
    ins_clean = ins.replace("smallint unsigned", "smallint")
    
    # Write to file
    with open(os.path.join(output_dir, f"{table}.sql"), "a", encoding="utf-8") as f:
        f.write(ins_clean + "\n")

print(f"✅ Split {len(inserts)} inserts into {output_dir}/<table>.sql")




