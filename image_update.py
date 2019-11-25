import os
import subprocess
import re
import json
import sys

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
    #hash from repos
    hash_line = get_hash()
    #hash from local
    try:
        current_hash = get_current_hash(image, version)    
    except:
        current_hash = None

    hashes = []
    hashes.append(hash_line)
    hashes.append(current_hash)
    return hashes

def give_messages(hash_line, current_hash, image, version):
    print("Checking image: " + image +" Version: " + version)
    if current_hash == None:
        print("Error getting image repos")
        print("Perhaps this is a custom image from a Dockerfile?")
        return
    if hash_line == None:
        print("Error: This is not an official image, so its newest version cannot be found")
    else:
        #Does this image line up with the most recent repos?
        if hash_line == current_hash:
            print("image is up to date")

            #Is this version in sync with the "latest" tag
            if version != "latest":
                print("Checking for latest update")
                hashes = check_if_latest(image, "latest")
                if(hashes[0]== current_hash):
                    print("Version is up to date with latest")
                    return "N"
                else:
                    print("There is a new version available")
                    return "A"
            return "N"
        else:
            print("There is a new version available")
            return "A"

def get_images():
    #subprocess.call(["./init.sh"])
    f = open ("input.txt", "w+")
    subprocess.call(["docker", "images"], stdout=f)
    f.close()
    fd = open ("input.txt", "r")

    rows = len(fd.readlines())
    allImages = []
    fd = open("input.txt","r")
    for i in range(rows):
        line = fd.readline()
        line = line.strip("\n")
        line = line.split(" ")
        line = list(filter(None, line))
        allImages.append(line)

    return allImages

#Get latest docker version online
def get_docker_version():
    f = open("d_version.txt","w+")
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
    dv = re.search("[0-9]+.[0-9]+.[0-9]+", docker_version)
    return(dv.group(0))    


def update_image(image):
    f = open("logs.txt", "w+")
    subprocess.call(["docker", "pull", image],stdout = f, stderr=subprocess.DEVNULL)
    #sub = image.find(":")
    #image = image[0:sub]
    #print (image)



#Main Runner
'''
Flags:
    -ua Update all images possible
    -ul only update latest images
    -uv only update images with a specific version tag
    -h list options and info
'''
def main():
    areFlags = False
    if(len(sys.argv)>1):
        areFlags = True
        if(sys.argv[1]=="-h"):
            print("\n\n\nYo! So this is version 0.9 of Docker Image Updater!")
            print("This handy program will check your local docker images version against the official docker image")
            print("Flags:\n\t-ua Update all images possible\n\t-ul only update latest images\n\t-uv only update images with a specific version tag\n\t-h list options and info\n\n")
            return

    to_update_all = []
    allImages = get_images()
    num_of_images = len(allImages)
    for i in range (1,num_of_images):
        print("\n------------------------------------------\n")
        image = allImages[i][0]
        version = allImages[i][1]
        if version == "<none>":
            print(image+"This is an outdated container!")
            print("Run docker rmi -f <image> ")
        else:
            hashes = check_if_latest(image, version)
            hash_line = hashes[0]
            current_line = hashes[1]
            need_to_update = give_messages(hash_line, current_line, image, version)
            full_name = image + ":" + version
            if need_to_update == "A":
                to_update_all.append(full_name)

    print("\n------------------------------------------\n")

    print("Getting Docker version\n")
    recent_version = get_docker_version()
    system_version = get_local_docker_version()
    print("System version: "+system_version)
    print("Most recent version: "+recent_version+"\n")
    
    print("\n------------------------------------------\n")

    print("\tReport\n")
    print("Images to update:\n")
    for image in to_update_all:
        print(image)
    
    print("\nDocker Version:\n")
    if(recent_version != system_version):
        print("Your Docker version is out of date!")
        print("System version: "+system_version)
        print("Most recent version: "+recent_version+"\n")
    else:
        print("Docker is all up to date!")
        print("Version: "+system_version)
    
    print("\nBesides that, everything looks good!\n")

    if(areFlags==True):
        print("\n\n Time to Update!\n")
    else:
        return
    if(sys.argv[1]=="-ul"):
        print("Updating images with the 'latest' tag")
        for image in to_update_all:
            if image.find("latest"):
                print("Updating image: "+image)
                update_image(image)
                print("Successfully updated image: "+image + "\n")

    elif(sys.argv[1]=="-uv"):
        print("Updating images with a specific version")
        for image in to_update_all:
            if not(image.find("latest")):
                print("Updating image: "+image)
                update_image(image)
                print("Successfully updated image: "+image+"\n")

    elif(sys.argv[1]=="-ua"):
        for image in to_update_all:
            print("Updating image: "+image)
            update_image(image)
            print("Successfully updated image: "+image+"\n")
                
    print("Images are up to date!")

if __name__=='__main__':
    main()
