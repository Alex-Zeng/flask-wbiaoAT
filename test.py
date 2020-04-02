def uniqueOccurrences(arr):
    s_arr = set(arr)
    new_list = []
    for i in s_arr:
        count = 0
        for k in arr:
            if i == k:
                count += 1
        new_list.append(count)

    return True if len(set(new_list)) == len(new_list) else False

if __name__ == '__main__':
    arr = [1, 2, 2,2, 1, 1, 3]
    result = uniqueOccurrences(arr)
    print(result)
