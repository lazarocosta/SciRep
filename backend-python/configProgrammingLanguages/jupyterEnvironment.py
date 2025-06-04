import os
import re
from stdlib_list import stdlib_list
from settings import fileIsAnImage


def jupyterDependenciesToInstall(projectFiles):
    pythonDependencies = []
    rDependencies = []

    # dirs=directories
    for file in os.listdir(projectFiles):
        # not an image and not a temporary file
        if not file.startswith('.') and not fileIsAnImage(file) and os.path.isfile(projectFiles + "/" + file):
            # print(os.access(file, os.R_OK))
            fq = open(projectFiles + "/" + file, "r")
            fileRead = fq.read()
            myRDependencies = re.findall('(?<=library\().*?(?=\))', fileRead, re.IGNORECASE)
            # pythonDependencies +=re.findall('(?<=import ).*?(?= as)', fileRead, re.IGNORECASE)
            myPythonDependencies = re.findall('(?<=from ).*?(?= import)', fileRead, re.IGNORECASE)
            # myPythonDependencies= re.findall('(?<=import ).*?(?= as)', fileRead, re.IGNORECASE)

            pythonDependencies += [dependencies.split('.')[0] for dependencies in myPythonDependencies]
            rDependencies += [dependencies.split('.')[0] for dependencies in myRDependencies]

            fq.close()

    pythonDependencies = [*set(pythonDependencies)]
    rDependencies = [*set(rDependencies)]
    return {"pythonDependencies": pythonDependencies,
            "rDependencies": rDependencies}


def createJupyterNotebookEnvironment(myProjectFolder, projectFiles):
    standardLibraries = stdlib_list("3.7")

    myReturn = jupyterDependenciesToInstall(projectFiles)
    pythonDependencies = myReturn["pythonDependencies"]
    rDependencies = myReturn["rDependencies"]

    print(pythonDependencies)
    print("rDependencies")
    print(rDependencies)

    f = open(myProjectFolder + "/Dockerfile", "a")
    f.write("FROM jupyter/all-spark-notebook:latest\n")
    f.write("WORKDIR /home/jovyan/\n")
    for dependency in pythonDependencies:
        if not dependency in standardLibraries:
            f.write("RUN pip install --no-cache-dir -U " + dependency + "\n")
    for dependency in rDependencies:
        # f.write("RUN R -e \"install.packages('" + dependency + "', repos='http://cran.rstudio.com/', dependencies=TRUE)\"\n")
        f.write(
            "RUN R -e \"install.packages('" + dependency + "', repos='http://cran.rstudio.com/', warn.conflicts = FALSE)\"\n", )
        # f.write("RUN R -e 'install.packages(\"" + dependency + "\")\'\n")
        # if not dependency in standardLibraries:
        #    f.write("RUN pip install --no-cache-dir -U " + dependency + "\n")
    f.close()
    return



# FROM jupyter/all-spark-notebook:python-3.10
#
# WORKDIR /home/jovyan/
#
# WORKDIR /files
# COPY ./files .
#
#
# USER root

#TODO nao está a ativar este ambiente
#RUN conda create -n py37 python=3.7
#RUN source activate py37
#RUN ipython kernel install

# COPY --from=maven:3.6.3-openjdk-11-slim /usr/local/openjdk-11 /usr/local/my-java
# ENV JAVA_HOME /usr/local/my-java
# RUN update-alternatives --install /usr/bin/java java /usr/local/my-java/bin/java 2000
# #update-alternatives --list java
#
# COPY --from=maven:3.6.3-openjdk-11-slim /usr/share/maven /usr/share/maven
# ENV M2_HOME /usr/share/maven
# ENV M2 $M2_HOME/bin
# RUN update-alternatives --install /usr/bin/mvn mvn /usr/share/maven/bin/mvn 1
#
#
#
# RUN pip install -r requirements.txt
