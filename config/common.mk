ifeq ($(NGC_VENDOR),)
$(warning ************* installing my addons ***************************)

# FDroid
PRODUCT_PACKAGES += \
    FDroid \
    FDroidPrivilegedExtension \
    privapp-permissions-org.fdroid.fdroid.privileged.xml \
    additional_repos.xml \
    80-fdroid.sh

# microG
PRODUCT_PACKAGES += \
    GmsCore \
    GsfProxy \
    FakeStore \
    NetworkLocation \
    MozillaNlpBackend \
    NominatimNlpBackend \
    OpenBmapNlpBackend \
    DroidGuard \
    com.google.android.maps.jar \
    com.google.android.maps.xml \
    privapp-permissions-com.google.android.gms.xml \
    privapp-permissions-com.android.vending.xml \
    10-mapsapi.sh

# NGC overlays
PRODUCT_ENFORCE_RRO_EXCLUDED_OVERLAYS += vendor/ngc4622/overlay
DEVICE_PACKAGE_OVERLAYS += vendor/ngc4622/overlay
else
$(warning ************* not installing my addons ***************************)
endif
