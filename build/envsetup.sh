# Setup build environment for Arch Linux
if [ -f "/etc/arch-release" ]; then
    if [ ! -f "$ANDROID_BUILD_TOP/tools/arch/python/bin/python2" ]; then
        virtualenv2 $ANDROID_BUILD_TOP/tools/arch/python > /dev/null
    fi
    source $ANDROID_BUILD_TOP/tools/arch/python/bin/activate
    ln -s /usr/lib/python2.7/* $ANDROID_BUILD_TOP/tools/arch/python/lib/python2.7/ &> /dev/null
    export USE_CLANG_PLATFORM_BUILD=true
fi
