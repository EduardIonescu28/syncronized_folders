import os.path
import sys
import time
import shutil
from os import listdir

f1_path = sys.argv[1]
f2_path = sys.argv[2]

shutil.rmtree(f2_path)

try:
    sync_interval = int(sys.argv[3])
except ValueError:
    print("sys.argv[3] should be integer")
    exit()

log_file_path = sys.argv[4]

if not os.path.isdir(f1_path):
    os.mkdir(f1_path)

if not os.path.isdir(f2_path):
    os.mkdir(f2_path)

log_file = open(log_file_path, "a")
log_file.truncate(0)

vector_date_modify_initial = []

for file in os.listdir(f1_path):
    append_value = file + " ///// " + time.ctime(os.path.getmtime(f1_path + "/" + file))
    vector_date_modify_initial.append(append_value)
    try:
        shutil.copy(f1_path + "\\" + file, f2_path + "\\" + file)
    except PermissionError:
        try:
            shutil.copytree(f1_path + "\\" + file, f2_path + "\\" + file)
        except FileExistsError:
            pass

while 1:

    current_vector = []
    replica_vector = []
    for file in os.listdir(f1_path):
        append_value = file + " ///// " + time.ctime(os.path.getmtime(f1_path + "/" + file))
        current_vector.append(append_value)

    # A new file was created
    for current_file in current_vector:
        check = False
        for file_in_old_vector in vector_date_modify_initial:
            if current_file.split(" ///// ")[0] == file_in_old_vector.split(" ///// ")[0]:
                check = True
                break
        if not check:
            print("A new file was added to the folder: " + current_file.split(" ///// ")[0])
            log_file.write("A new file was added to the folder: " + current_file.split(" ///// ")[0] + "\n")
            try:
                shutil.copy(f1_path + "\\" + current_file.split(" ///// ")[0],
                        f2_path + "\\" + current_file.split(" ///// ")[0])
            except PermissionError:
                shutil.copytree(f1_path + "\\" + current_file.split(" ///// ")[0],
                        f2_path + "\\" + current_file.split(" ///// ")[0])

    # A file was deleted
    for current_file in vector_date_modify_initial:
        check = True
        for file_in_old_vector in current_vector:
            if current_file.split(" ///// ")[0] == file_in_old_vector.split(" ///// ")[0]:
                check = False
        if check:
            print("A file was deleted from the folder: " + current_file.split(" ///// ")[0])
            log_file.write("A file was deleted from the folder: " + current_file.split(" ///// ")[0] + "\n")
            try:
                os.remove(f2_path + "\\" + current_file.split(" ///// ")[0])
            except PermissionError:
                try:
                    shutil.rmtree(f2_path + "\\" + current_file.split(" ///// ")[0])
                except PermissionError:
                    exit()

    # date modify source > date modify replica
    # init vector replica
    for file in os.listdir(f2_path):
        append_value = file + " ///// " + time.ctime(os.path.getmtime(f2_path + "/" + file))
        replica_vector.append(append_value)

    for current_source_file in current_vector:
        for current_replica_file in replica_vector:
            if current_source_file.split(" ///// ")[0] == current_replica_file.split(" ///// ")[0] and \
                    current_source_file.split(" ///// ")[1] > current_replica_file.split(" ///// ")[1]:
                print("The next file was modified: " + current_source_file.split(" ///// ")[0])
                log_file.write("The next file was modified: " + current_source_file.split(" ///// ")[0] + "\n")
                try:
                    os.remove(f2_path + "\\" + current_source_file.split(" ///// ")[0])
                except PermissionError:
                    try:
                        shutil.rmtree(f2_path + "\\" + current_source_file.split(" ///// ")[0])
                    except PermissionError:
                        exit()
                try:
                    shutil.copy(f1_path + "\\" + current_source_file.split(" ///// ")[0],
                                f2_path + "\\" + current_source_file.split(" ///// ")[0])
                except PermissionError:
                    try:
                        shutil.copytree(f1_path + "\\" + current_source_file.split(" ///// ")[0],
                                        f2_path + "\\" + current_source_file.split(" ///// ")[0])
                    except FileExistsError:
                        pass

        # if a file is accidentally deleted from replica
        for current_file in current_vector:
            check = True
            for replica_file in replica_vector:
                if current_file.split(" ///// ")[0] == replica_file.split(" ///// ")[0]:
                    check = False
            if check:
                print("The next file was deleted by accident from replica: " + current_file.split(" ///// ")[0])
                log_file.write("The next file was deleted by accident from replica: " + current_file.split(" ///// ")[0] + "\n")
                try:
                    shutil.copy(f1_path + "\\" + current_file.split(" ///// ")[0],
                                f2_path + "\\" + current_file.split(" ///// ")[0])
                    append_value = current_file + " ///// " + time.ctime(os.path.getmtime(f2_path + "\\" + current_file.split(" ///// ")[0]))
                    replica_vector.append(append_value)
                except PermissionError:
                    try:
                        shutil.copytree(f1_path + "\\" + current_file.split(" ///// ")[0],
                                        f2_path + "\\" + current_file.split(" ///// ")[0])
                        append_value = current_file + " ///// " + time.ctime(
                            os.path.getmtime(f2_path + "\\" + current_file.split(" ///// ")[0]))
                        replica_vector.append(append_value)

                    except FileExistsError:
                        pass

    vector_date_modify_initial = current_vector

    time.sleep(int(sync_interval))
