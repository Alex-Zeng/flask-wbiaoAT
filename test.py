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
    png = '123'
    filename='D:\workspace\UIAtuoTest\base\screen_shot\TestLog-190\MUMU模拟4723-登录\20200403114736步骤_7_密码登录-点击登录按钮.txt'
    with open(filename, 'wb') as f:
        f.write(png)
