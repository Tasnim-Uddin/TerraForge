# start = -2
# end = 3
# for layer in range(1, 4):  # Number of iterations
#     all_x_shifts = range(start, end)
#     print(start, end)
#     for x_shift in all_x_shifts:
#         print("Iteration:", layer, "x:", x_shift)
#     start += 1
#     end -= 1


chunks = {}
chunks[1] = "dog"
chunks[1] = "cat"
print(chunks)

breaking_item = "leaf_block"
if breaking_item == ("wood_plank" or "leaf_block"):
    print("YESSSS")