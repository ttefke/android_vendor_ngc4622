include $(CLEAR_VARS)

# Conditionally build su
WITH_SU := true

# Call all subdir makefiles
include $(call all-subdir-makefiles)
