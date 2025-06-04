from settings import copyFilesAndClose


def perlEnvironment_linux(myProjectFolder, perlVersionString, linuxVersion):
    file = open(myProjectFolder + "/Dockerfile", "a")
    perlVersion = perlVersionString.split("Perl:")[1]
    #TODO verificar
    ##["Perl:5.21.1.1", "Perl:5.30.3.1", "Perl:5.28.2.1", "Perl:5.26.3.1", "Perl:5.24.4.1"]
    allowPerlVersion = ["5.21.1.1", "5.24.4.1", "5.26.3.1", "5.28.2.1", "5.30.3.1"]

    if perlVersion not in allowPerlVersion:
        file.close()
        raise ValueError("Perl version is not available")

    if linuxVersion is not None:
        my_linuxVersion = linuxVersion
    else:
        my_linuxVersion = "22.04"
        my_linuxVersion = "18.04"
        my_linuxVersion = "20.04"

        file.write("FROM ubuntu:" + my_linuxVersion + "\n")
        file.write("RUN apt update\n")
        file.write("RUN apt upgrade -y\n")

    file.write("RUN apt install perl -y\n")

    copyFilesAndClose(file, linuxVersion)

    return my_linuxVersion


def perlEnvironment_windows(myProjectFolder, perlVersionString, windowsVersion):
    file = open(myProjectFolder + "/Dockerfile", "a")
    perlVersion = perlVersionString.split("Perl:")[1]
    allowPerlVersion = ["5.21.1.1", "5.24.4.1", "5.26.3.1", "5.28.2.1", "5.30.3.1"]

    if perlVersion not in allowPerlVersion:
        file.close()
        raise ValueError("Perl version is not available")

    if windowsVersion is not None:
        my_windowsVersion = windowsVersion
    else:
        my_windowsVersion = True

        file.write("# Use the Windows Server Core image as the base image\n")
        file.write("FROM mcr.microsoft.com/windows/servercore:ltsc2019\n")

    file.write("# Set up environment variables\n")
    file.write("ENV PERL_VERSION " + perlVersion + "\n")
    file.write("ENV PERL_PATH C:/Perl64\n")

    # https://strawberryperl.com/releases.html
    file.write("# Download and extract Strawberry Perl\n")
    file.write(
        "ADD https://strawberryperl.com/download/${PERL_VERSION}/strawberry-perl-${PERL_VERSION}-64bit.zip C:/perl.zip\n")
    file.write('''RUN powershell -Command "Expand-Archive -Path 'C:\perl.zip' -DestinationPath 'C:\Perl64'"''')
    file.write('''RUN powershell -Command "Remove-Item -Path 'c:\perl.zip'"''')

    file.write("# Add Perl to the PATH\n")
    file.write('RUN setx /M PATH "%PATH%;%PERL_PATH%\perl\bin"\n')

    copyFilesAndClose(file, windowsVersion)
    return my_windowsVersion


