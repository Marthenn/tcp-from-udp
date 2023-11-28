import hashlib

def calculate_md5(file_path):
    with open(file_path, 'rb') as file:
        data = file.read()
        md5_hash = hashlib.md5()
        md5_hash.update(data)
        return md5_hash.hexdigest()

def compare_files(file_path1, file_path2):
    return calculate_md5(file_path1) == calculate_md5(file_path2)

if __name__ == '__main__':
    file1 = input('Enter the path of the first file: ')
    file2 = input('Enter the path of the second file: ')
    if compare_files(file1, file2):
        print('Files are identical')
    else:
        print('Files are not identical')
