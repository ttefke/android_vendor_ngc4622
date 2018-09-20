#
# Copyright (C) 2018 Tobias Tefke
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Simple tool for copying proprietary files from system images

from enum import Enum
from os import system, path
import os
import shutil
import sys

copyFiles = [] # will contain files that can be easily copied
buildFiles = [] # will contain files that need to be rebuild as prebuilts
removedFiles = [] # deleted multilib files from buildFiles
prebuiltPackages = [] # contains the package names; refers to buildFiles

# define enum for file types
class BuildPrebuilt(Enum):
    so = 1
    apk = 2
    jar = 3
    sbin_executable = 4
    executable = 5
    undefined = 6
    
def unmountSystem():
    print("Unmounting system image")
    cmd = str("sudo umount " + sysImgMountPoint)
    system(cmd)
    

"""
getBlobsFromFile(file):

file: file to pull blobs from

this function adds the blobs that can be
easily copied to copyFiles and the ones
that need to be rebuilt as prebuilts to
buildFiles
"""
def getBlobsFromFile(file):
    with open(file, "r") as blobs:
        for line in blobs:
            line = line.strip()
            # skip empty lines
            if not line:
                continue
            # skip comments
            if line.startswith("#"):
                continue
            # add files to be build as prebuilts to buildFiles
            if line.startswith("-"):
                buildFiles.append(line[1:])
            # add all other files to the copy list
            else:
                copyFiles.append(line)

"""
getBringupYear(file)

file: file that contains the bringup year
      (usually setup-makefiles.sh)
      
returns: bringup year

reads the bringup year from the given file
and returns it
"""
def getBringupYear(file):
    with open(file, "r") as year:
        for line in year:
            line = line.strip()
            # skip empty lines
            if not line:
                continue
            # we only care about INITIAL_COPYRIGHT_YEAR
            if not line.startswith("INITIAL_COPYRIGHT_YEAR"):
                continue
            year = line.split("=")[1]
            print("Bringup year: " + year)
            return year
    # Bringup year not found
    print("ERROR: Bringup year not found")
    unmountSystem()
    sys.exit(0)

"""
def createSkeletonVendorDir(path)

path: path to the vendor directory

generates an empty vendor directory
or emties an existing one
"""
def createSkeletonVendorDir(path):
    print("Creating vendor directory")
    # Delete vendor directory contents if present
    if os.path.exists(path):
        for vendor_file in os.listdir(path):
            file_path = os.path.join(path, vendor_file)
            try:
                # do not delete the git folder
                if file_path.endswith(".git"):
                    continue
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)
                print("ERROR: Deleting vendor folder contents failed")
                unmountSystem()
                sys.exit(0)
    else:
        os.makedirs(path)

"""
generateApacheHeader(year, vendor, device)

year: bingup year
vendor: vendor of the device
device: the device

returns an Apache 2.0 header
"""
def generateApacheHeader(year, vendor, device):
    copyright = "# Copyright (C) " + year + " The LineageOS Project"
    realApacheHeader = """#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License."""
    autogeneration = "# This file is generated by device/" + vendor + "/" + device + "/setup-makefiles.sh"
    completeHeader = copyright + "\n" + realApacheHeader + "\n\n" + autogeneration + "\n"
    return completeHeader

"""
getName(module, module_type)

module: path to the module
module_type: type of the module

returns a name that can be used as
LOCAL_NAME and appends the name
to the list of files to be rebuild
in the build process
"""
def getName(module, module_type):
    # get name of module
    local_module = module.split("/")[-1]
    if (not module_type == BuildPrebuilt.sbin_executable) or (not module_type == BuildPrebuilt.executable):
        if module_type == BuildPrebuilt.so:
            local_module = local_module[:-3]
        else:
            # JAR or APK
            local_module = local_module[:-4]
    
    # remove possible rootfs postfix
    if module_type == BuildPrebuilt.sbin_executable:
        local_module = local_module.split(";")[0]

    prebuiltPackages.append(local_module)
    return local_module

"""
isVendorModule(module, declaration)

module: path to the module
declaration: declaration for a file to be rebuild

adds LOCAL_VENDOR_MODULE to the declaration if
the module is a module located in the vendor
folder/partition and returns the declaration
"""
def isVendorModule(module, declaration):
    if "vendor/" in module:
        declaration += "LOCAL_VENDOR_MODULE := true\n"
    
    return declaration

"""
writeXXXPrebuiltModule(module, vendor)

module: path to the module
vendor: device vendor

writes the neccessary code for rebuilding
the module handed over to the method
to Android.mk
"""
def writeSoPrebuiltModule(module, vendor):
    #get name of the module
    local_module = getName(module, BuildPrebuilt.so)
    
    # arm libs: find out if there is an arm64 lib
    arm32_lib = False
    arm64_lib = False
    module32 = ""
    module64 = ""
    if "lib/" in module:
        arm32_lib = True
        module32 = module
        module64 = module.replace("lib/", "lib64/")
        if module64 in buildFiles:
            arm64_lib = True
            buildFiles.remove(module64)
            removedFiles.append(module64)
    elif "lib64/" in module:
        arm64_lib = True
        module64 = module
        module32 = module.replace("lib64/", "lib/")
        if module32 in buildFiles:
            arm32_lib = True
            buildFiles.remove(module32)
            removedFiles.append(module32)
    else:
        print("ERROR: could not get architecture of the library " + module)
        unmountSystem()
        sys.exit(0)
    
    declaration = "\ninclude $(CLEAR_VARS)\n"
    declaration += "LOCAL_MODULE := " + local_module + "\n"
    declaration += "LOCAL_MODULE_OWNER := " + vendor + "\n"
    
    # arm and arm64 library present
    if (arm32_lib == True) and (arm64_lib == True):
        declaration += "LOCAL_SRC_FILES_64 := proprietary/" + module64 + "\n"
        declaration += "LOCAL_SRC_FILES_32 := proprietary/" + module32 + "\n"
        declaration += "LOCAL_MULTILIB := both\n"
    # only arm library present
    elif (arm32_lib == True) and (arm64_lib == False):
        declaration += "LOCAL_SRC_FILES := proprietary/" + module32 + "\n"
        declaration += "LOCAL_MULTILIB := 32\n"
    # only arm64 library present
    elif (arm32_lib == False) and (arm64_lib == True):
        declaration += "LOCAL_SRC_FILES := proprietary/" + module64 + "\n"
        declaration += "LOCAL_MULTILIB := 64\n"
    else:
        print("ERROR: no library present on module " + module)
        unmountSystem()
        sys.exit(0)
    
    declaration += "LOCAL_MODULE_TAGS := optional\n"
    declaration += "LOCAL_MODULE_CLASS := SHARED_LIBRARIES\n"
    declaration += "LOCAL_MODULE_SUFFIX := .so\n"
    
    declaration = isVendorModule(module, declaration)
    
    declaration += "include $(BUILD_PREBUILT)\n"
    
    return declaration

def writeApkPrebuiltModule(module, vendor):
    #get name of the module
    local_module = getName(module, BuildPrebuilt.apk)
    
    # join together declaration
    declaration = "\ninclude $(CLEAR_VARS)\n"
    declaration += "LOCAL_MODULE := " + local_module + "\n"
    declaration += "LOCAL_MODULE_OWNER := " + vendor + "\n"
    declaration += "LOCAL_SRC_FILES := proprietary/" + module + "\n"
    declaration += "LOCAL_CERTIFICATE := platform\n"
    declaration += "LOCAL_MODULE_TAGS := optional\n"
    declaration += "LOCAL_MODULE_CLASS := APPS\n"
    declaration += "LOCAL_DEX_PREOPT := false\n"
    declaration += "LOCAL_MODULE_SUFFIX := .apk\n"
    
    # check if module is privileged
    if "priv-app/" in module:
        declaration += "LOCAL_PRIVILEGED_MODULE := true\n"
    
    declaration = isVendorModule(module, declaration)
    
    declaration += "include $(BUILD_PREBUILT)\n"
    
    return declaration

def writeJarPrebuiltModule(module, vendor):
    #get name of the module
    local_module = getName(module, BuildPrebuilt.jar)
    
    # join together declaration
    declaration = "\ninclude $(CLEAR_VARS)\n"
    declaration += "LOCAL_MODULE := " + local_module + "\n"
    declaration += "LOCAL_MODULE_OWNER := " + vendor + "\n"
    declaration += "LOCAL_SRC_FILES := proprietary/" + module + "\n"
    declaration += "LOCAL_CERTIFICATE := platform\n"
    declaration += "LOCAL_MODULE_TAGS := optional\n"
    declaration += "LOCAL_MODULE_CLASS := JAVA_LIBRARIES\n"
    declaration += "LOCAL_MODULE_SUFFIX := .jar\n"
    
    declaration = isVendorModule(module, declaration)
    
    declaration += "include $(BUILD_PREBUILT)\n"
    
    return declaration

def writeSbinPrebuiltModule(module, vendor):
    # get name of the module
    local_module = getName(module, BuildPrebuilt.sbin_executable)

    # join together declaration
    declaration = "\ninclude $(CLEAR_VARS)\n"
    declaration += "LOCAL_MODULE := " + local_module + "\n"
    declaration += "LOCAL_MODULE_OWNER := " + vendor + "\n"
    declaration += "LOCAL_MODULE_PATH := $(TARGET_ROOT_OUT_SBIN)\n"
    declaration += "LOCAL_UNSTRIPPED_PATH := $(TARGET_ROOT_OUT_SBIN_UNSTRIPPED)\n"
    declaration += "LOCAL_SRC_FILES := proprietary/rootfs/sbin/" + local_module + "\n"
    declaration += "LOCAL_MODULE_TAGS := optional\n"
    declaration += "LOCAL_MODULE_CLASS := EXECUTABLES\n"
    declaration += "include $(BUILD_PREBUILT)\n"
    
    return declaration

def writeBinPrebuiltModule(module, vendor):
    # get name of the module
    local_module = getName(module, BuildPrebuilt.bin_executable)

    # join together declaration
    declaration = "\ninclude $(CLEAR_VARS)\n"
    declaration += "LOCAL_MODULE := " + local_module + "\n"
    declaration += "LOCAL_MODULE_OWNER := " + vendor + "\n"
    declaration += "LOCAL_SRC_FILES := proprietary/" + module + "\n"
    declaration += "LOCAL_MODULE_TAGS := optional\n"
    declaration += "LOCAL_MODULE_CLASS := EXECUTABLES\n"
    declaration += "include $(BUILD_PREBUILT)\n"
    
    return declaration

def writePrebuiltModule(module, vendor):
    # split first part of the module if the module is being moved
    if ":" in module:
        module = module.split(":")[1]

    # get type of prebuilt file
    prebuiltType = BuildPrebuilt.undefined
    if module.endswith(".so"):
        return writeSoPrebuiltModule(module, vendor)
    elif module.endswith(".apk"):
        return writeApkPrebuiltModule(module, vendor)
    elif module.endswith(".jar"):
        return writeJarPrebuiltModule(module, vendor)
    elif "sbin/" in module:
        return writeSbinPrebuiltModule(module, vendor)
    elif "bin/" in module:
        return writeBinPrebuiltModule(module, vendor)
    else:
        # error if file type is still undefined
        print("ERROR: file type of " + module + " is undefined")
        unmountSystem()
        sys.exit(0)

"""
create XXXMk(path, year, vendor, device)

path: vendor path pointing to the blobs
year: initial bringup year
vendor: device vendor
device: the device

creates the makefiles
"""
def createAndroidMk(path, year, vendor, device):
    filename = path + "/Android.mk"
    with open(filename, "w") as androidmk:
        # write Ápache header
        androidmk.write("{}".format(generateApacheHeader(year, vendor, device)))
        # write local path declaration
        androidmk.write("{}".format("\nLOCAL_PATH := $(call my-dir)\n"))
        # write guard begin
        androidmk.write("{}".format("\nifeq ($(TARGET_DEVICE)," + device + ")\n"))
        # write prebuilt module declaration
        for module in buildFiles:
            androidmk.write("{}".format(writePrebuiltModule(module, vendor)))
        # write guard end
        androidmk.write("{}".format("\nendif\n"))
    print("Written Android.mk")


def createBoardConfigVendorMk(path, year, vendor, device):
    filename = path + "/BoardConfigVendor.mk"
    with open(filename, "w") as bcvmk:
        # write Apache header
        bcvmk.write("{}\n".format(generateApacheHeader(year, vendor, device)))
    print("Written BoardConfigVendor.mk")


def createDeviceVendorMk(path, year, vendor, device):
    filename = path + "/" + device + "-vendor.mk"
    with open(filename, "w") as vendormk:
        # write Apache header
        vendormk.write("{}".format(generateApacheHeader(year, vendor, device)))
        # write PRODUCT_COPY_FILES command
        vendormk.write("{}".format("\nPRODUCT_COPY_FILES += \\\n"))
        
        # generate new list that drops old paths if blob is being moved
        realBlobs = []
        for element in copyFiles:
            # drop old path if needed
            if ":" in element:
                element = element.split(":")[1]
            # add element to list
            realBlobs.append(element)
        
        # sort list
        realBlobs.sort()
        
        # add location for the build system
        for element in realBlobs[:-1]:
            element = "    vendor/htc/oce/proprietary/" + element + ":system/" + element + " \\\n"
            vendormk.write("{}".format(element))
        element = "    vendor/htc/oce/proprietary/" + realBlobs[-1] + ":system/" + realBlobs[-1] + "\n"
        vendormk.write("{}".format(element))
        
        # add packages that need to be rebuilt
        vendormk.write("{}".format("\nPRODUCT_PACKAGES += \\\n"))
        
        for element in prebuiltPackages[:-1]:
            element = "    " + element + " \\\n"
            vendormk.write("{}".format(element))
        element = "    " + prebuiltPackages[-1] + "\n"
        vendormk.write("{}".format(element))
        
    print("Written {}-vendor.mk".format(device))

"""
copyProprietaryFiles(vendor_dir, sysImgLocation)

vendor_dir: directory where the blobs are stored
sysImgLocation: mount point of the system image

copies the proprietary files from the system image
to the vendor directory
"""
def copyProprietaryFiles(vendor_dir, sysImgLocation):
    allFiles = copyFiles
    allFiles.extend(buildFiles)
    allFiles.extend(removedFiles)
    for element in allFiles:
        # skip sbin files
        if "sbin/" in element:
            print("Skipped sbin file {}".format(element.split(";")[0]))
            continue
        if ":" in element:
            source = sysImgLocation + "/" + element.split(":")[0]
            destination = vendor_dir + "/proprietary/" + element.split(":")[1]
        else:
            source = sysImgLocation + "/" + element
            destination = vendor_dir + "/proprietary/" + element
        
        try:
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.copyfile(source, destination)
        except FileNotFoundError as e:
            print("Could not copy file {}".format(element))

# Give warning about paths
print("WARNING: all paths have to be absolute!")

# get system image localtion
sysImgLocation = str(input("Enter the location of the system image: "))

# get mount point for system image
sysImgMountPoint = str(input("Enter a mount point for the image: "))

# get LineageOS source directory
srcDir = str(input("Enter the location of the LineageOS source directory: "))

# get vendor name
vendor = str(input("Enter the vendor name: "))

# get device name
device = str(input("Enter the device name: "))

# mount image
cmd = str("sudo mount -r -o loop " + sysImgLocation + " " + sysImgMountPoint)
print("Root privileges needed for mounting the image")

if system(cmd) == 0:
    print("Successfully mounted system image")
else:
    print("ERROR: System image could not be mounted")
    sys.exit(0)

# declare possible filenames
device_dir = srcDir + "/device/" + vendor + "/" + device

proprietary_files = str(device_dir + "/proprietary-files.txt")
proprietary_files_qc = str(device_dir + "/proprietary-files-qc.txt")
proprietary_files_qc_perf = str(device_dir + "/proprietary-files-qc-perf.txt")

if path.isfile(proprietary_files):
    print(str("Found list of proprietary files in " + proprietary_files))
    getBlobsFromFile(proprietary_files)

if path.isfile(proprietary_files_qc):
    print(str("Found list of proprietary files in " + proprietary_files_qc))
    getBlobsFromFile(proprietary_files_qc)

if path.isfile(proprietary_files_qc_perf):
    print(str("Found list of proprietary files in " + proprietary_files_qc_perf))
    getBlobsFromFile(proprietary_files_qc_perf)

# create vendor directory
vendor_dir = srcDir + "/vendor/" + vendor + "/" + device
createSkeletonVendorDir(vendor_dir)

# get bringup year
year = getBringupYear(str(device_dir) + "/setup-makefiles.sh")

# generate Android.mk
createAndroidMk(vendor_dir, year, vendor, device)

# generate BoardConfigVendor.mk
createBoardConfigVendorMk(vendor_dir, year, vendor, device)

# generate device-vendor.mk
createDeviceVendorMk(vendor_dir, year, vendor, device)

# copy files
copyProprietaryFiles(vendor_dir, sysImgMountPoint)

# unmount the sytem image
unmountSystem()

print("Done")

