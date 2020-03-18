ifeq ($(NGC_VENDOR),)
$(warning ************* installing my addons ***************************)

# F-Droid
PRODUCT_PACKAGES += \
    FDroid \
    FDroidPrivilegedExtension \
    additional_repos.xml

# microg
PRODUCT_PACKAGES += \
    GmsCore \
    GsfProxy \
    FakeStore \
    OpenBmapNlpBackend \
    OpenWeatherMapWeatherProvider \
    MozillaNlpBackend \
    NominatimNlpBackend \
    NetworkLocation \
    UnifiedNlp \
    com.google.android.maps.jar \
    10-mapsapi.sh \
    80-fdroid.sh

# Privileged permissions whitelists
LOCAL_PACKAGES += \
    privapp-permissions-org.fdroid.fdroid.privileged.xml \
    privapp-permissions-com.android.vending.xml \
    privapp-permissions-com.google.android.gms.xml \
    com.google.android.maps.xml

# NGC overlays
PRODUCT_ENFORCE_RRO_EXCLUDED_OVERLAYS += vendor/ngc4622/overlay
DEVICE_PACKAGE_OVERLAYS += vendor/ngc4622/overlay
else
$(warning ************* not installing my addons ***************************)
endif
