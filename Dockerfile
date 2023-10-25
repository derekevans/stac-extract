FROM ubuntu:22.04

RUN apt-get update

# Necessary for installing tzdata non-interactively
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install tools 
RUN apt-get install build-essential software-properties-common cmake wget tzdata -y

# Build PROJ, GEOS, and GDAL from source
RUN mkdir /software
WORKDIR /software

# Build and install openjpeg (driver necessary for .jp2 support)
RUN apt-get install liblcms2-dev libtiff-dev libpng-dev libz-dev -y && \
    wget https://github.com/uclouvain/openjpeg/archive/refs/tags/v2.5.0.tar.gz && \
    tar xvf v2.5.0.tar.gz && \
    cd openjpeg-2.5.0 && \
    mkdir build && \
    cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    make && \
    make install && \
    make clean && \
    cd /software && \
    rm v2.5.0.tar.gz && \
    rm -r openjpeg-2.5.0

# Build and install PROJ
RUN apt-get install libsqlite3-dev sqlite3 libtiff-dev libcurl4-openssl-dev -y && \
    wget https://download.osgeo.org/proj/proj-9.3.0.tar.gz && \
    tar xvf proj-9.3.0.tar.gz && \
    cd proj-9.3.0 && \
    mkdir build && \
    cd build && \
    cmake .. && \
    cmake --build . && \
    cmake --build . --target install && \
    cd /software && \
    rm proj-9.3.0.tar.gz && \
    rm -r proj-9.3.0

# Build and install GEOS
RUN apt-get install bzip2 -y && \
    wget https://download.osgeo.org/geos/geos-3.12.0.tar.bz2 && \
    tar xvfj geos-3.12.0.tar.bz2 && \
    cd geos-3.12.0 && \
    mkdir build && \
    cd build  && \
    cmake .. && \
    make && \
    make install && \
    cd /software && \
    rm geos-3.12.0.tar.bz2 && \
    rm -r geos-3.12.0

# Build and install GDAL
RUN wget https://github.com/OSGeo/gdal/releases/download/v3.7.2/gdal-3.7.2.tar.gz && \
    tar xvf gdal-3.7.2.tar.gz && \
    cd gdal-3.7.2 && \
    mkdir build && \
    cd build  && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    cmake --build . && \
    cmake --build . --target install && \
    cd /software && \
    rm gdal-3.7.2.tar.gz && \
    rm -r gdal-3.7.2

# Install python3.11
RUN add-apt-repository ppa:deadsnakes/ppa -y && \
    apt-get update -y && \
    apt-get install python3.11 python3.11-venv python3.11-dev python3.11-distutils libffi-dev -y

# Misc. tools
RUN apt-get install vim -y

# Create ubuntu user, switch to this user, and cd to user home directory
RUN useradd --create-home --shell /bin/bash ubuntu
USER ubuntu
ENV HOME=/home/ubuntu
WORKDIR $HOME

# Install venv
RUN python3.11 -m venv ~/python/envs/pysatimg && \
    echo "source $HOME/python/envs/pysatimg/bin/activate" >> $HOME/.bashrc

WORKDIR $HOME
CMD ["/bin/bash"]