#!/bin/bash

# Store root directory
rootdir=$(pwd)

# Patches directory
vnddir=$(pwd)/vendor/ngc4622/patches

# Apply microg patches
patchdir="frameworks/base"

for dir in $patchdir ; do
    cd $rootdir
    cd $patchdir
    git am $vnddir/$patchdir/*.patch
done

cd $rootdir

# Source my configuration files
patchdir="vendor/lineage"

for dir in $patchdir ; do
    cd $rootdir
    cd $patchdir
    git am $vnddir/$patchdir/*.patch
done

cd $rootdir
