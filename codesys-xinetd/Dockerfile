#
# Stage 1:
# Install CODESYS in debian stretch with wine-development version
#
FROM debian:stretch

RUN dpkg --add-architecture i386
RUN apt-get update && \
    apt-get install -y wine32-development wine64-development wget subversion winbind python-requests cabextract xvfb xdotool jwm procps

RUN useradd -ms /bin/bash wineuser

# Configure locales
RUN apt-get install -y locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8

# Install CODESYS
USER wineuser
WORKDIR "/home/wineuser"
ADD install.sh /home/wineuser/
RUN ./install.sh --xvfb; test -f /home/wineuser/.wine.cds/drive_c/CODESYS/CODESYS/Common/CODESYS.exe

USER root
RUN apt-get install -y tigervnc-standalone-server

#
# Stage 2
# Copy CODESYS installation into debian testing, as stretch has
# a bug in xinetd. The limits for nofile can't be configured.
#
FROM debian:testing
ENV WINEPREFIX=/home/wineuser/.wine.cds

# Setup VNC with xinetd
EXPOSE 8050
USER root
RUN dpkg --add-architecture i386
RUN apt-get update && \
    apt-get install -y wine32-development wine64-development wget subversion winbind python-requests cabextract xvfb xdotool jwm procps \
    tigervnc-standalone-server xinetd ratpoison \
    locales
    
# Configure locales
RUN useradd -ms /bin/bash wineuser
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8

ADD Xvnc /etc/xinetd.d/Xvnc
ADD xinetd-vnc /xinetd-vnc

USER wineuser
COPY --from=0 /home/wineuser/.wine.cds /home/wineuser/.wine.cds
USER root
RUN chown -R wineuser:users /home/wineuser/.wine.cds


ENTRYPOINT [ "xinetd", "-dontfork" ]

