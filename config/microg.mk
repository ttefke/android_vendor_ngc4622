# Include microg packages

# F-Droid
PRODUCT_PACKAGES += \
    FDroid

# F-Droid privileged extension
PRODUCT_PACKAGES += \
    FDroidPrivilegedExtension

# microg
PRODUCT_PACKAGES += \
    GmsCore \
    GsfProxy \
    FakeStore \
    OpenBmapNlpBackend \
    OpenWeatherMapWeatherProvider \
    NominatimNlpBackend \
    com.google.android.maps.jar \
    10-mapsapi.sh \
    80-fdroid.sh

# Privileged permissions whitelists
LOCAL_PACKAGES += \
    privapp-permissions-org.fdroid.fdroid.privileged.xml \
    privapp-permissions-com.android.vending.xml \
    privapp-permissions-com.google.android.gms.xml \
    com.google.android.maps.xml
