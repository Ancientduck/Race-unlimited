import os

# path to the folder containing your .py files
folder_path = "."

total_lines = 0
total_size = 0
for filename in os.listdir(folder_path):
    if filename.endswith(".py"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            total_lines += len(lines)
            size = os.path.getsize(file_path)/1000
            total_size += size
            print(f"{filename}: {len(lines)} lines and size: {size} KB\n")
            #print(f'{filename}, size: {size} KB ')

print(f"\nTotal lines in all .py files: {total_lines}")
print(f"\nTotal size = {total_size} KB")
