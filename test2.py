

if __name__ == "__main__":
    device_name ='BLA-AL00'
    device_name = (
        device_name.decode('utf-8')
            .replace("\n", "")
            .replace("\r", "")
    )
    print(device_name)