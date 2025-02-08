from threading import Thread
import random


# Single threaded merge sort:
def merge_sort(nums):
    def helper(l, r):
        nonlocal temp
        if l == r:
            return

        # Step 1: Divide: Break poblem into smaller halves recursively
        m = (l + r) // 2
        helper(l, m)
        helper(m + 1, r)

        # Step 2: Conquer: Merge the subproblems to get final solution
        i, j, k = l, m + 1, l
        while i <= m and j <= r:
            if nums[i] <= nums[j]:
                temp[k] = nums[
                    i
                ]  # No race condition since all threads modify different parts of temp!
                i += 1
            else:
                temp[k] = nums[j]
                j += 1
            k += 1

        while i <= m:
            temp[k] = nums[i]
            i += 1
            k += 1
        while j <= r:
            temp[k] = nums[j]
            j += 1
            k += 1

        # Note since all threads are modifying disjoint indicies, no race condition!
        nums[l : r + 1] = temp[l : r + 1]

    temp = [0] * len(nums)
    helper(0, len(nums) - 1)


# Multithreaded merge sort
def multithreaded_merge_sort(nums):
    def helper(l, r):
        nonlocal temp
        if l == r:
            return

        # Step 1: Divide: Break poblem into smaller halves recursively
        m = (l + r) // 2

        # Change 1: Create worker threads to do these independent pieces of work
        worker1 = Thread(target=helper, args=(l, m))
        worker2 = Thread(target=helper, args=(m + 1, r))
        worker1.start()
        worker2.start()
        worker1.join()
        worker2.join()

        # Step 2: Conquer: Merge the subproblems to get final solution
        i, j, k = l, m + 1, l
        while i <= m and j <= r:
            if nums[i] <= nums[j]:
                temp[k] = nums[i]
                i += 1
            else:
                temp[k] = nums[j]
                j += 1
            k += 1

        while i <= m:
            temp[k] = nums[i]
            i += 1
            k += 1
        while j <= r:
            temp[k] = nums[j]
            j += 1
            k += 1

        nums[l : r + 1] = temp[l : r + 1]

    temp = [0] * len(nums)
    helper(0, len(nums) - 1)


def create_data(size):
    unsorted_list = [None] * size
    random.seed()

    for i in range(0, size):
        unsorted_list[i] = random.randint(0, 1000)

    return unsorted_list


def print_list(lst):
    end = len(lst)
    for i in range(0, end):
        print(lst[i], end=" ")


if __name__ == "__main__":
    size = 12
    unsorted_list = create_data(size)
    unsorted_list_copy = unsorted_list[:]

    print("Unsorted:")
    print_list(unsorted_list)
    multithreaded_merge_sort(unsorted_list)
    print("\n\nSorted multithreaded:")
    print_list(unsorted_list)
    merge_sort(unsorted_list_copy)
    print("\n\nSorted single threaded:")
    print_list(unsorted_list_copy)

    print("\n\nTwo list equal?")
    print(unsorted_list == unsorted_list_copy)
