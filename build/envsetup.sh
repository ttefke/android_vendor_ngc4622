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

function dessert()
{
    setupJack
    DEVICE=$1
    breakfast $DEVICE
    if [ $? -eq 0 ]; then
        m -j$2 target-files-package otatools
        if [ -z ${OUT_DIR_COMMON_BASE+x} ]; then
            OUTPATH=$ANDROID_BUILD_TOP/out/dist/$DEVICE
            RECOVERY=$ANDROID_BUILD_TOP/out/target/product/$DEVICE/recovery.img
        else
            OUTPATH=$OUT_DIR_COMMON_BASE/dist/$DEVICE
            RECOVERY=$OUT_DIR_COMMON_BASE/target/product/$DEVICE/recovery.img
        fi
        mkdir -p $OUTPATH
        cp $RECOVERY $OUTPATH/recovery_$DEVICE.img
        ./build/tools/releasetools/sign_target_files_apks -o -d ~/.android-certs \
            $OUT/obj/PACKAGING/target_files_intermediates/*-target_files-*.zip \
            signed-target_files.zip
        ./build/tools/releasetools/ota_from_target_files -k ~/.android-certs/releasekey \
            --block --backup=true \
            signed-target_files.zip \
            $OUTPATH/lineage_signed_${DEVICE}_$(date +"%d-%b-%Y-%H-%M").zip
        rm signed-target_files.zip
    else
        echo "No such item in dessert menu. Try 'breakfast'"
        return 1
    fi
    return $?
}

export WITH_SU=true
