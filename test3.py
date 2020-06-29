import requests
import tempfile
import subprocess

def download_file(target_url):
    """ download file to temp path, and return its file path for further usage """
    resp = requests.get(target_url,stream=True)
    chunk_length = 16 * 1024
    with tempfile.NamedTemporaryFile(mode='w+b', delete=False) as f:
        file_name = f.name
        for buf in resp.iter_content(chunk_length):
            f.write(buf)
    return file_name

def get_abi():
    abi = subprocess.getoutput(
        "{} -s {} shell getprop ro.product.cpu.abi".format("adb", "127.0.0.1:7555")
    )
    print("11{}--".format(abi.strip()))
def get_sdk():
    sdk = subprocess.getoutput(
        "{} -s {} shell getprop ro.build.version.sdk".format("adb", "127.0.0.1:7555")
    )
    print("11{}--".format(sdk.strip()))

if __name__ == '__main__':
    target_url = "https://github.com/openatx/stf-binaries/tree/master/node_modules/minicap-prebuilt/prebuilt/x86/bin/minicap"

    file_name = download_file(target_url)
    print(file_name)
    # get_abi()
    # get_sdk()