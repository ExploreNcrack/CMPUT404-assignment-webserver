import os

def prevent_access_to_other_directory(path_string):
    """
    This function checks the path string if it contains ../ 
    Return:
    True:
        it does not access to other directory
    False:
        it tries to access to directory outside of the www
    """        
    # get the www absolute path 
    current_dir = os.path.realpath("www")
    # retrieve all the children directory absolute path
    www_child_dirctories = []
    for sub_dir in os.walk(current_dir):
        www_child_dirctories.append(sub_dir[0])
    # www_child_dirctories = [x[0] for x in os.walk(current_dir)]
    abosulte_request_path = os.path.realpath(path_string)
    # if given path is a file
    if os.path.isfile(path_string):
        # get the file's directory
        dir_of_request_path = os.path.dirname(abosulte_request_path)
        # check if the file's directory is a child directory of www
        if dir_of_request_path not in www_child_dirctories:
            return False
    # if given path is a directory        
    if os.path.isdir(path_string):
        if abosulte_request_path not in www_child_dirctories:
            return False

    return True

a=prevent_access_to_other_directory("www/deep/../..")
print(a)
