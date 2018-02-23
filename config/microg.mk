# Include microg packages

# F-Droid
PRODUCT_PACKAGES += \
    FDroid

# F-Droid privileged extension
PRODUCT_PACKAGES += \
    FDroidPrivilegedExtension \
    permissions_org.fdroid.fdroid.privileged.xml

# microg
PRODUCT_PACKAGES += \
    GmsCore \
    GsfProxy \
    FakeStore \
    OpenBmapNlpBackend \
    OpenWeatherMapWeatherProvider \
    NominatimNlpBackend \
    com.google.android.maps.jar \
    com.google.android.maps.xml \
    10-mapsapi.sh \
    80-fdroid.sh
