import os
import subprocess

# import necessario
# from stdlib_list import stdlib_list
# standardLibraries = stdlib_list("3.7")
#
#
# def getDependenciesToInstall(savePath, diretoryToCheck, diretorysToIgnore):
#     dependencias = []
#     proc = subprocess.Popen(
#         #        ['pipreqs', '--ignore', ','.join(diretorysToIgnore), '--encoding', 'utf-8', '--savepath', savePath,
#         ['pipreqs', '--ignore', ','.join(diretorysToIgnore), '--encoding', 'utf-8',
#          #       ['pip','-V',
#          diretoryToCheck],
#         shell=False,
#         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#     for line in proc.stdout:
#         x = 0
#         dependencias.append(line.decode().strip())
#         print(line.decode().strip())
#     return dependencias
#

def readDependenciesFile(file_location):
    f = open(file_location, "r")
    for x in f:
        print('myLog:'+x.rstrip('\n'))
    f.close()


# to get the current working directory
currentDirectory = os.getcwd()
#print(currentDirectory)
# getDependenciesToInstall("C:/Users/lazar/Desktop/python-mini-projects-master/projects/All_links_from_given_webpage")

# TODO
# recebo do utilizador
# cuidado tem que ser apenas ficheiros de dados caso contrario dá problemas
# diretorysToIgnore = ['model', 'controllers']
diretorysToIgnore = []

requirementsFile = "requirements.txt"

#getDependenciesToInstall(requirementsFile, currentDirectory, diretorysToIgnore)
readDependenciesFile(requirementsFile)
