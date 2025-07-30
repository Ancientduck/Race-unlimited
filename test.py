import time
start = time.time()
for i in range(6_600_000):
    pass  # empty loop
end = time.time()

print(f"Took {end - start:.2f} seconds")
