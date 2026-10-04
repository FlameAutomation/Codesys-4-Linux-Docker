#
# Install CODESYS in debian buster with wine-development version
# Note: We sometimes need to switch users from "wineuser" to root and back.
#       The reason is, that things inside linux need to be installed as root,
#       while things inside of wine, need to be installed as wineuser.
#
FROM debian:bullseye

RUN dpkg --add-architecture i386
RUN apt-get update && \
    apt-get install -y wine32 wine64 wget subversion winbind cabextract msitools xvfb xdotool jwm procps

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
ADD install2.sh /home/wineuser/
RUN ./install2.sh --silent; \
    test -f /home/wineuser/.wine.cds/drive_c/CODESYS/CODESYS/Common/CODESYS.exe

# Add automation scripts, which can be used for CI/CD jobs
ADD codesys /usr/local/bin/codesys
ADD codesyscontrol /usr/local/bin/codesyscontrol
ADD scripts /usr/local/share/codesys


# Install Linux SL package (in IDE and the runtime)
RUN codesys install https://store.codesys.com/ftp_download/3S/LinuxSL/2302000005/3.5.16.0/CODESYS%20Control%20for%20Linux%20SL%203.5.16.0.package

USER root
#RUN dpkg -i "/home/wineuser/.wine.cds/drive_c/users/wineuser/CODESYS Control for Linux SL/Dependency/codemeter-lite_7.0.3918.500_amd64.deb"
#RUN dpkg -i "/home/wineuser/.wine.cds/drive_c/users/wineuser/CODESYS Control for Linux SL/Delivery/codesyscontrol_x64_linux_V3.5.16.0.deb"

USER wineuser


# basic test of the image
RUN codesys test

CMD [ "echo" ]
