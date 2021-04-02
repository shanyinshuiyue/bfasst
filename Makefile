install: packages install_fasm2bels install_yosys

packages:
	sudo apt install -y \
		make \
		python3.8-dev \
		python3-pip \
		virtualenv \
		libncurses5 \
		swig \
		python3-venv \
		default-jre-headless \
		uuid-dev \
		libantlr4-runtime-dev
	
	sudo python3 -m pip install -r requirements.txt

capnproto:
	cd /tmp && curl -O https://capnproto.org/capnproto-c++-0.8.0.tar.gz
	cd /tmp && tar zxf capnproto-c++-0.8.0.tar.gz
	cd /tmp/capnproto-c++-0.8.0 && ./configure
	cd /tmp/capnproto-c++-0.8.0 && make -j6 check
	cd /tmp/capnproto-c++-0.8.0 && sudo make install

capnproto_java:
	cd /tmp && git clone https://github.com/capnproto/capnproto-java
	cd /tmp/capnproto-java && make
	cd /tmp/capnproto-java && sudo make install


rapidwright:
	cd third_party && wget http://www.rapidwright.io/docs/_downloads/rapidwright-installer.jar
	source third_party/rapidwright.sh
	cd third_party/Rapidwright/interchange

install_fasm2bels:
	git submodule init
	git submodule update
	cd third_party/fasm2bels && make env
	cd third_party/fasm2bels && make build
	cd third_party/fasm2bels && make test-py


install_yosys:
	# Yosys
	sudo apt install -y \
		build-essential \
		clang \
		bison \
		flex \
		libreadline-dev \
		gawk \
		tcl-dev \
		libffi-dev \
		graphviz \
		xdot \
		pkg-config \
		libboost-system-dev \
		libboost-python-dev \
		libboost-filesystem-dev \
		zlib1g-dev

	cd third_party/yosys && make -j8


format:
	find ./scripts -iname "*.py" -exec black -l 100 {} \;


