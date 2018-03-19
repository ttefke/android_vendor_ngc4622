#!/bin/bash

# Store this directory
CWD=$(pwd)

# Get source root from working directory
TOP=$CWD/../../../

# Patch build/core in order to include our envsetup.sh
patchdir="build/core"

for dir in $patchdir ; do
    cd $TOP
    cd $patchdir
    git am $CWD/$patchdir/*.patch
done

# Apply microg patches
patchdir="frameworks/base"

for dir in $patchdir ; do
    cd $TOP
    cd $patchdir
    git am $CWD/$patchdir/*.patch
done

# Include overlay with lineage overlays
patchdir="vendor/lineage"

for dir in $patchdir ; do
    cd $TOP
    cd $patchdir
    git am $CWD/$patchdir/*.patch
done

# Update checkstyle for Arch Linux
if [ -f "/etc/arch-release" ]; then
    patchdir="prebuilts/checkstyle"

    for dir in $patchdir ; do
        cd $TOP
        cd $patchdir
        git am $CWD/$patchdir/*.patch
    done
fi

cd $CWD
