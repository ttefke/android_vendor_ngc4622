#!/bin/bash

# Store root directory
rootdir=$(pwd)

# Patches directory
vnddir=$(pwd)/vendor/ngc4622/patches


# Update art for Arch Linux
if [ -f "/etc/arch-release" ]; then
    patchdir="art"

    for dir in $patchdir ; do
        cd $rootdir
        cd $patchdir
        git am $vnddir/$patchdir/*.patch
    done
fi

# Patch build/core in order to include our envsetup.sh
patchdir="build/core"

for dir in $patchdir ; do
    cd $rootdir
    cd $patchdir
    git am $vnddir/$patchdir/*.patch
done

# Apply microg patches
patchdir="frameworks/base"

for dir in $patchdir ; do
    cd $rootdir
    cd $patchdir
    git am $vnddir/$patchdir/*.patch
done

# Include overlay with cm overlays
patchdir="vendor/cm"

for dir in $patchdir ; do
    cd $rootdir
    cd $patchdir
    git am $vnddir/$patchdir/*.patch
done

cd $rootdir
