# Custom build commands
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
    # 1 thread per core
    threads=$(expr $cores / 2)
    m -j$threads "$@"
}

function dessert()
{
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

export WITH_SU=true
