#!/bin/bash

# Store root directory
rootdir=$(pwd)

# Patches directory
vnddir=$(pwd)/vendor/ngc4622/patches

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

# Include overlay with lineage overlays
patchdir="vendor/lineage"

for dir in $patchdir ; do
    cd $rootdir
    cd $patchdir
    git am $vnddir/$patchdir/*.patch
done

cd $rootdir
