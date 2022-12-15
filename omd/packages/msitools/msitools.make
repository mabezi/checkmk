MSITOOLS := msitools
MSITOOLS_VERS := 0.94
MSITOOLS_DIR := msitools-$(MSITOOLS_VERS)
# Increase this to enforce a recreation of the build cache
MSITOOLS_BUILD_ID := 0

# TODO: Extract LCAB to dedicated package
LCAB_VERSION := 1.0b12
LCAB_DIR     := lcab-$(LCAB_VERSION)

#LCAB_INSTALL_DIR := $(INTERMEDIATE_INSTALL_BASE)/$(LCAB_DIR)
LCAB_BUILD_DIR := $(PACKAGE_BUILD_DIR)/$(LCAB_DIR)
#LCAB_WORK_DIR := $(PACKAGE_WORK_DIR)/$(LCAB_DIR)

MSITOOLS_PATCHING := $(BUILD_HELPER_DIR)/$(MSITOOLS_DIR)-patching
MSITOOLS_BUILD := $(BUILD_HELPER_DIR)/$(MSITOOLS_DIR)-build
MSITOOLS_INTERMEDIATE_INSTALL := $(BUILD_HELPER_DIR)/$(MSITOOLS_DIR)-install-intermediate
MSITOOLS_CACHE_PKG_PROCESS := $(BUILD_HELPER_DIR)/$(MSITOOLS_DIR)-cache-pkg-process
MSITOOLS_INSTALL := $(BUILD_HELPER_DIR)/$(MSITOOLS_DIR)-install

MSITOOLS_INSTALL_DIR := $(INTERMEDIATE_INSTALL_BASE)/$(MSITOOLS_DIR)
MSITOOLS_BUILD_DIR := $(PACKAGE_BUILD_DIR)/$(MSITOOLS_DIR)
#MSITOOLS_WORK_DIR := $(PACKAGE_WORK_DIR)/$(MSITOOLS_DIR)

ifneq ($(filter $(DISTRO_CODE),sles15 sles15sp1 sles15sp2 sles15sp3 sles15sp4),)
GSF_CONFIGURE_VARS := GSF_LIBS="$(PACKAGE_LIBGSF_LDFLAGS)" GSF_CFLAGS="$(PACKAGE_LIBGSF_CFLAGS)"
else
GSF_CONFIGURE_VARS :=
endif

$(MSITOOLS_BUILD): $(LIBGSF_INTERMEDIATE_INSTALL) $(MSITOOLS_PATCHING) $(BUILD_HELPER_DIR)/$(LCAB_DIR)-unpack
	cd $(MSITOOLS_BUILD_DIR) && \
          $(GSF_CONFIGURE_VARS) ./configure --prefix="" ; \
	  $(MAKE) -C libmsi ; \
	  $(MAKE) msibuild ; \
	  $(MAKE) msiinfo ; \
	cd $(LCAB_BUILD_DIR) && ./configure --prefix="" && $(MAKE)
	$(TOUCH) $@

MSITOOLS_CACHE_PKG_PATH := $(call cache_pkg_path,$(MSITOOLS_DIR),$(MSITOOLS_BUILD_ID))

$(MSITOOLS_CACHE_PKG_PATH):
	$(call pack_pkg_archive,$@,$(MSITOOLS_DIR),$(MSITOOLS_BUILD_ID),$(MSITOOLS_INTERMEDIATE_INSTALL))

$(MSITOOLS_CACHE_PKG_PROCESS): $(MSITOOLS_CACHE_PKG_PATH)
	$(call unpack_pkg_archive,$(MSITOOLS_CACHE_PKG_PATH),$(MSITOOLS_DIR))
	$(call upload_pkg_archive,$(MSITOOLS_CACHE_PKG_PATH),$(MSITOOLS_DIR),$(MSITOOLS_BUILD_ID))
	$(TOUCH) $@

$(MSITOOLS_INTERMEDIATE_INSTALL): $(MSITOOLS_BUILD)
	$(MKDIR) $(MSITOOLS_INSTALL_DIR)/bin
	install -m 755 $(MSITOOLS_BUILD_DIR)/.libs/msiinfo $(MSITOOLS_INSTALL_DIR)/bin
	install -m 755 $(MSITOOLS_BUILD_DIR)/.libs/msibuild $(MSITOOLS_INSTALL_DIR)/bin
	install -m 755 $(LCAB_BUILD_DIR)/lcab $(MSITOOLS_INSTALL_DIR)/bin

	$(MKDIR) $(MSITOOLS_INSTALL_DIR)/lib
	install -m 755 $(MSITOOLS_BUILD_DIR)/libmsi/.libs/libmsi.so* $(MSITOOLS_INSTALL_DIR)/lib
	$(TOUCH) $@

$(MSITOOLS_INSTALL): $(MSITOOLS_CACHE_PKG_PROCESS)
	$(RSYNC) $(MSITOOLS_INSTALL_DIR)/ $(DESTDIR)$(OMD_ROOT)/
	$(TOUCH) $@
