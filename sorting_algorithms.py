
def bubble_sort(arr):
    """
    Performs in-place Bubble Sort on a list.
    Stops early if no swaps occur in a pass.
    """
    n = len(arr)
    for end in range(n - 1, 0, -1):
        swapped = False
        for i in range(end):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                swapped = True
        if not swapped:
            break


def selection_sort(arr):
    """
    Performs in-place Selection Sort.
    Repeatedly selects the minimum element and puts it in place.
    """
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]


def insertion_sort(arr):
    """
    Performs in-place Insertion Sort.
    Builds the sorted array one item at a time.
    """
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key


# Sample input
original = [6, 6, 2]

print("Original list:")
print(original)

# Bubble Sort
arr1 = original.copy()
bubble_sort(arr1)
print("\nBubble Sort result:")
print(arr1)

# Selection Sort
arr2 = original.copy()
selection_sort(arr2)
print("\nSelection Sort result:")
print(arr2)

# Insertion Sort
arr3 = original.copy()
insertion_sort(arr3)
print("\nInsertion Sort result:")
print(arr3)

# Python built-in sort (in-place)
arr4 = original.copy()
arr4.sort()
print("\nPython .sort() result:")
print(arr4)

# Python built-in sorted() (returns new list)
arr5 = sorted(original)
print("\nPython sorted() result (non-in-place):")
print(arr5)
