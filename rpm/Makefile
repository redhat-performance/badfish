PYTHON := python3
BUILD_HELPER := ./build-helper

VERSION = $(shell $(BUILD_HELPER) --version)
RELEASE = $(shell $(BUILD_HELPER) --release)
DATE = $(shell date +'%a %b %d %Y')
TARBALL = badfish-$(VERSION).tar.gz

all: badfish.spec badfish-$(VERSION).tar.gz

tarball: $(TARBALL)

.PHONY: $(TARBALL)
$(TARBALL):
	rm -f $(TARBALL)
	( cd .. && git archive --prefix badfish-$(VERSION)/ HEAD ) \
	    | gzip > "$@"

badfish.spec: badfish.spec.tpl
	@echo "  GEN $@" ; \
	sed -e "s|@VERSION@|$(VERSION)|g" \
	    -e "s|@RELEASE@|$(RELEASE)|g" \
	    -e "s|@DATE@|$(DATE)|g" \
	    $< > $@.output ; \
	mv "$@.output" "$@" # move when successful

srpm: all
	dir=`pwd` ; \
	rm *.src.rpm ; \
	rpmbuild --define "_sourcedir $$dir" \
		 --define "_rpmdir    $$dir" \
		 --define "_builddir  $$dir" \
		 --define "_specdir   $$dir" \
		 --define "_srcrpmdir $$dir" \
	     -bs *.spec

clean:
	rm -rf *.src.rpm *.tar.gz *.spec noarch

test: tarball badfish.spec
	@echo "Moving tarball to rpmbuild/SOURCES directory"
	mkdir -p ~/rpmbuild/SOURCES
	cp $(TARBALL) ~/rpmbuild/SOURCES/
	@echo "Tarball $(TARBALL) successfully moved to rpmbuild/SOURCES"
	@echo "Building source RPM from spec file"
	SRPM_PATH=$$(rpmbuild -bs badfish.spec | grep "Wrote:" | cut -d' ' -f2) && \
	echo "Source RPM build completed: $$SRPM_PATH" && \
	echo "Running mock build with the generated SRPM" && \
	mock -r fedora-rawhide-x86_64 -n $$SRPM_PATH && \
	echo "Mock build completed successfully"
