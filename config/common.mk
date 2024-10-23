ifeq ($(NGC_VENDOR),)
$(warning ************* installing my addons ***************************)

# FDroid
PRODUCT_PACKAGES += \
    FDroid \
    FDroidPrivilegedExtension \
    privapp-permissions-org.fdroid.fdroid.privileged.xml \
    additional_repos.xml

# microG
PRODUCT_PACKAGES += \
    FakeStore \
    privapp-permissions-com.android.vending.xml \
    default-permissions-com.android.vending.xml \
    GmsCore \
    privapp-permissions-com.google.android.gms.xml \
    default-permissions-com.google.android.gms.xml \
    sysconfig-com.google.android.gms.xml \
    GsfProxy \
    IchnaeaNlpBackend \
    NominatimGeocoderBackend

# NGC overlays
PRODUCT_ENFORCE_RRO_EXCLUDED_OVERLAYS += vendor/ngc4622/overlay
DEVICE_PACKAGE_OVERLAYS += vendor/ngc4622/overlay
else
$(warning ************* not installing my addons ***************************)
endif
