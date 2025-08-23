import chardet

with open("jobs.json", "rb") as f:
    raw = f.read(10000)  # read first 10KB

print(chardet.detect(raw))
