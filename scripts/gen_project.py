import argparse
import shutil
import os

CopyFolders = ["cmake", "include", "source", "tests"]
CopyFiles = ["CMakeLists.txt", ".gitattributes"]

def copy_project_files(originPath, targetPath):
    if not os.path.exists(targetPath):
        os.mkdir(targetPath)

    for copyFolder in CopyFolders:
        originFolderPath = os.path.join(originPath, copyFolder)
        targetFolderPath = os.path.join(targetPath, copyFolder)
        print(f"Copy from: {originFolderPath} \n to: {targetFolderPath}")
        try:
            shutil.copytree(originFolderPath, targetFolderPath, dirs_exist_ok=True)
        except:
            pass
    for copyFile in CopyFiles:
        originFolderPath = os.path.join(originPath, copyFile)
        targetFolderPath = os.path.join(targetPath, copyFile)
        try:
            shutil.copyfile(originFolderPath, targetFolderPath)
        except:
            pass


def process_main_cmakelists(path):
    project_index = 2

    with open(path) as file:
        idx = 1
        for line in file:
            line = line.rstrip()
            if idx == project_index:
                pass
                

def process_tests_cmakelists(path):
    with open(path) as file:
        for line in file:
            line = line.rstrip()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=True)
    parser.add_argument('--path', required=True)

    args = parser.parse_args()

    targetPath = os.path.join(args.path, args.name)
    print(f"Output path: {targetPath}")
    head, tail = os.path.split(os.path.dirname(os.path.realpath(__file__)))
    originPath = head

    copy_project_files(originPath, targetPath)

    incl_folder_path = os.path.join(targetPath, "include/folder")
    target_incl_folder_path = os.path.join(targetPath, f"include/{args.name}")
    shutil.move(incl_folder_path, target_incl_folder_path)

    mainCmakeFile = os.path.join(targetPath, "CMakeLists.txt")
    testsCmakeFile = os.path.join(targetPath, "tests/CMakeLists.txt")

    # process_main_cmakelists(mainCmakeFile)
    # process_tests_cmakelists(testsCmakeFile)

