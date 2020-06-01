

if __name__ == "__main__":
    device_dict = {}
    user = {'username':{'1':'2'}}
    user2 = {'3':'4'}
    device_dict.update(user)
    device_dict.get('username',0).update(user2)
    print(device_dict)