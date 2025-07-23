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


def merge_sort(arr):
    """
    Performs Merge Sort (not in-place).
    Recursively divides the list and merges sorted halves.
    """
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    return merge(left, right)


def merge(left, right):
    """
    Helper function to merge two sorted lists.
    """
    result = []
    i = j = 0

    # Merge the two halves
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # Append any remaining elements
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# Sample input
original = [6, 6, 2, 3, 2]

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

# Merge Sort (not in-place)
arr4 = original.copy()
arr4_sorted = merge_sort(arr4)
print("\nMerge Sort result:")
print(arr4_sorted)

# Python built-in sort (in-place)
arr5 = original.copy()
arr5.sort()
print("\nPython .sort() result:")
print(arr5)

# Python built-in sorted() (returns new list)
arr6 = sorted(original)
print("\nPython sorted() result (non-in-place):")
print(arr6)
