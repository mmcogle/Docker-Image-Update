import os
import subprocess
import re
import json

#def update docker

#def update runc

#get hash from the repos
def get_hash():
    string = ""
    with open("raw.txt") as f:
        for line in f:
            s = re.search("^\$ docker pull ([a-zA-Z0-9._-]*@[a-zA-Z0-9._:-]*)$", line)
            if s:
                string = (s.group(1))
                return string
                
#get hash from docker inspect
def get_current_hash(image, version):
    string = ""
    full_version = image + ":" + version
    inspect_out = subprocess.check_output(["docker","inspect", full_version])
    JSON_dict = json.loads(inspect_out)
    current_hash = JSON_dict[0]["RepoDigests"]
    return current_hash[0]
    #inspect_out = inspect_out.strip('[')
    #inspect_out = inspect_out.strip(']')
    #print(inspect_out)
    
        

def check_if_latest(image, version):
    #print("Checking image: " + image +" Version: " + version)
    url = "https://raw.githubusercontent.com/docker-library/repo-info/master/repos/"
    url = url + image
    tag = "/remote/"
    version_file = version + ".md"
    tag += version_file
    url += tag
    f = open("raw.txt", "w")
    raw_text = subprocess.call(["wget","-O","-",url], stdout = f, stderr = subprocess.DEVNULL)
    f.close()
    hash_line = get_hash()
    current_hash = get_current_hash(image, version)    
    #print(current_hash)
    #print(hash_line)
    #give_messages(hash_line, current_hash, image, version)
    hashes = []
    hashes.append(hash_line)
    hashes.append(current_hash)
    return hashes

def give_messages(hash_line, current_hash, image, version):
    print("Checking image: " + image +" Version: " + version)
    if hash_line == current_hash:
        print("image is up to date")
        if version != "latest":
            print("Checking for latest update")
            hashes = check_if_latest(image, "latest")
            if(hashes[0]== current_hash):
                print("Version is up to date with latest")
            else:
                print("There is a new version available")
    else:
        print("There is a new version available")

def get_images():
    fnull = open(os.devnull, 'w')
    subprocess.call(["./init.sh"])
    f = open ("input.txt", "w")
    images = subprocess.call(["docker", "images"], stdout=f)

    f.close()
    fd = open ("input.txt", "r")

    rows = len(fd.readlines())
    allImages = []
    fd = open("input.txt","r")
    for i in range(rows):
        line = fd.readline()
        line = line.strip("\n")
        line = line.split(" ")
        count =0
        size = len(line)
        line = list(filter(None, line))
        allImages.append(line)

    return allImages

#Get latest docker version online
def get_docker_version():
    f = open("d_version.txt","r+")
    url = "https://api.github.com/repos/docker/docker-ce/releases/latest"
    subprocess.call(["wget","-O","-",url], stdout = f, stderr = subprocess.DEVNULL)
    f.close()
    f = open("d_version.txt","r")
    docker_json = f.read()    
    JSON_dict = json.loads(docker_json)
    f.close()
    version = JSON_dict["name"]
    return version

def get_local_docker_version():
    docker_version = subprocess.check_output(["docker","-v"])    
    #docker_version = str(docker_version)
    docker_version = docker_version.strip()
    docker_version = str(docker_version)
    dv = re.search("", docker_version)
    
    print(dv.group(0))    

def main():
    allImages = get_images()
    num_of_images = len(allImages)
    for i in range (1,num_of_images):
        print("------------------------------------------")
        hashes = check_if_latest(allImages[i][0], allImages[i][1])
        hash_line = hashes[0]
        current_line = hashes[1]
        give_messages(hash_line, current_line, allImages[i][0], allImages[i][1])

    print("------------------------------------------")
    print("Getting Docker version")
    recent_version = get_docker_version()
    get_local_docker_version()

main()
