FROM ubuntu:20.04

MAINTAINER codinuum

RUN set -x && \
    useradd -r -s /bin/nologin cca && \
    mkdir -p /opt/cca/modules && \
    mkdir -p /var/lib/cca && \
    mkdir /root/src

COPY LICENSE /opt/cca/
COPY cca /opt/cca/
COPY regression_examples /opt/cca/regression_examples/
COPY configs /opt/cca/configs/

RUN set -x && \
    cd /opt/cca/ddutil && \
    rm conf.py common.sh && \
    mv conf.py.docker conf.py && \
    mv common.sh.docker common.sh && \
    cd /opt/cca/scripts && \
    rm siteconf.py && \
    mv siteconf.py.docker siteconf.py && \
    cd /opt/cca/esecfse2018 && \
    rm conf.py common.sh && \
    mv conf.py.docker conf.py && \
    mv common.sh.docker common.sh && \
    cd /root && \
    apt update && \
    env DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends gnupg2 ca-certificates && \
    echo "deb https://downloads.skewed.de/apt focal main" > /etc/apt/sources.list.d/gt.list && \
    apt-key adv --no-tty --keyserver keys.openpgp.org --recv-key 612DEFB798507F25 && \
    apt update && \
    env DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends \
            sudo \
            vim \
            opam \
            net-tools psmisc time \
            locales locales-all nkf \
            m4 flex bison automake autoconf \
            libtool pkg-config swig \
            libgmp-dev libssl-dev libz-dev libreadline-dev librdf0-dev libpcre3-dev unixodbc-dev \
            gawk gperf \
            sloccount \
            unixodbc \
            openjdk-8-jdk \
            ant ant-optional maven pcregrep \
            python3 python3-dev \
            python3-distutils \
            python3-psutil \
            python3-pygit2 \
            python3-svn \
            python3-distutils \
            python3-graph-tool \
            wget curl git subversion rsync && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python3 get-pip.py && \
    pip3 install pyodbc simplejson ortools javalang python-daemon && \
    rm get-pip.py && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-amd64

# For installing Defects4J

RUN set -x && \
    apt update && \
    env DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends \
        libdbi-perl libdbd-csv-perl liburi-perl libjson-perl libjson-parse-perl && \
    cd /opt && \
    git clone https://github.com/rjust/defects4j.git && \
    cd defects4j && \
    ./init.sh && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

ENV PATH $PATH:/opt/defects4j/framework/bin

# For installing Redland

RUN set -x && \
    cd /root && \
    git clone https://github.com/dajobe/redland-bindings && \
    cd redland-bindings && \
    ./autogen.sh --with-python=python3 && \
    make install && \
    cd /root && \
    rm -r redland-bindings

# For installing Virtuoso

RUN set -x && \
    cd /root && \
    git clone https://github.com/openlink/virtuoso-opensource && \
    cd virtuoso-opensource && \
    ./autogen.sh && \
    env CFLAGS='-O2 -m64' ./configure --prefix=/opt/virtuoso --with-layout=opt --with-readline=/usr --program-transform-name="s/isql/isql-v/" --disable-dbpedia-vad --disable-demo-vad --enable-fct-vad --enable-ods-vad --disable-sparqldemo-vad --disable-tutorial-vad --enable-isparql-vad --enable-rdfmappers-vad && \
    make && make install && \
    cd /root && \
    rm -r virtuoso-opensource

# For installing Diff/AST

COPY src /root/src/

RUN set -x && \
    cd /root && \
    opam init -y --disable-sandboxing && \
    eval $(opam config env) && \
    opam install -y camlzip cryptokit csv git-unix menhir ocamlnet pxp ulex uuidm pcre && \
    git clone https://github.com/codinuum/volt && \
    cd volt && sh configure && make all && make install && \
    cd /root && \
    rm -r volt && \
    cd src && \
    make && \
    cd ast/analyzing && \
    cp -r bin etc /opt/cca/ && \
    cp modules/Mverilog*.cmxs /opt/cca/modules/ && \
    cp modules/Mpython*.cmxs /opt/cca/modules/ && \
    cp modules/Mjava*.cmxs /opt/cca/modules/ && \
    cp modules/Mfortran*.cmxs /opt/cca/modules/ && \
    cp modules/Mcpp*.cmxs /opt/cca/modules/ && \
    cd /root && \
    rm -r src

#

CMD ["/bin/bash"]
