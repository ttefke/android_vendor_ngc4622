# Setup build environment for Arch Linux
if [ -f "/etc/arch-release" ]; then
    if [ ! -f "$ANDROID_BUILD_TOP/tools/arch/python/bin/python2" ]; then
        virtualenv2 $ANDROID_BUILD_TOP/tools/arch/python > /dev/null
    fi
    source $ANDROID_BUILD_TOP/tools/arch/python/bin/activate
    ln -s /usr/lib/python2.7/* $ANDROID_BUILD_TOP/tools/arch/python/lib/python2.7/ &> /dev/null
    export USE_CLANG_PLATFORM_BUILD=true
fi

# Build su
export WITH_SU=true

function setupJack() {
    # get amount of ram in kb
    ram=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    # convert to gb
    ram=$(expr $ram / 1000000)
    # add gb sign
    g="G"
    ram="$ram$g"
    # export to jack
    export ANDROID_JACK_VM_ARGS="-Dfile.encoding=UTF-8 -XX:+TieredCompilation -Xmx$ram"
}

function mkd() {
    # get number of cores
    cores=$(nproc)
    # 4 threads per core
    threads=$(expr $cores \* 4)
    m -j$threads "$@"
}

function setupCcache() {
    export USE_CCACHE=1
    echo "Enter location for cache files:"
    read location
    export CCACHE_DIR=$location
    echo "Enter max ccache size in GB:"
    read cachesize
    g="G"
    prebuilts/misc/linux-x86/ccache/ccache -M $cachesize$g
    export NGC_CCACHE_SETUP=1
}

function dessert()
{
    # setup ccache
    if [ "$NGC_CCACHE_SETUP" != "1" ]; then
        setupCcache
    fi
    # setup jack
    setupJack
    breakfast $*
    if [ $? -eq 0 ]; then
        mkd bacon
    else
        echo "No such item in dessert menu. Try 'breakfast'"
        return 1
    fi
    return $?
}
