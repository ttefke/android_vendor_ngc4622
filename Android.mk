include $(CLEAR_VARS)

# Conditionally build su
WITH_SU := true

# Add our overlays
DEVICE_PACKAGE_OVERLAYS += vendor/ngc4622/overlay

# Call all subdir makefiles
include $(call all-subdir-makefiles)
