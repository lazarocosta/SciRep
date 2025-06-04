#!/bin/bash
dockerfile="Dockerfile"
requerimentsFile="workspace/requirements.txt"


# Check the file is exists or not
if [ -f $dockerfile ]; then
   rm $dockerfile
   echo "$dockerfile was deleted"
fi

# Check the file is exists or not
if [ -f $requerimentsFile ]; then
   rm $requerimentsFile
   echo -e "$requerimentsFile was deleted\n"
fi
# docker image
echo -e "FROM jupyter/r-notebook \n">> $dockerfile

echo "WORKDIR /home/jovyan/" >> $dockerfile
echo -e "COPY workspace/requirements.txt .\n" >> $dockerfile


#########################################
######### Jupyter R  #########################
#########################################

export my_libraries=()

# loop between all the files inside the `work` folder
for notebookName in workspace/work/*.ipynb; do

   #echo "$notebookName"
   #get the library name and remove duplicate values
   libraries=`cat $notebookName | grep -oP '(?<=library\().*?(?=\))'`
   # shellcheck disable=SC2179
   my_libraries+=$libraries
   export my_libraries+=' '

done

# remove duplicates values
my_libraries=`echo "${my_libraries[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '`


#echo ${my_libraries[@]}
#echo $my_libraries

#echo ${sorted_unique_ids[0]}


#write all the libraries used to Dockerfile22
for library in $my_libraries; do
	echo "RUN R -e \"install.packages('$library', repos='http://cran.rstudio.com/')\"" >> $dockerfile
done


#########################################
######### Python #########################
#########################################
export python_libraries=()

for python_notebook in workspace/work/*.ipynb; do
   #get the library name and remove duplicate values
   export python_libraries+=` cat $python_notebook | grep -oP '(?<=import ).*? (?=as)'`

   export python_libraries+=` cat $python_notebook | grep -oP '(?<=from ).*? (?=import)'`

done

   #get the library name and remove duplicate values


export python_libraries=`echo "${python_libraries[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '`

export newarray=()



for python_libraries_elem in $python_libraries; do
   if [[ $python_libraries_elem =~ \. ]]; then
      newarray+=`echo $python_libraries_elem | grep -oP '.*?(?=\.\w*)'`
      newarray+=`echo ' '`
   else 
      newarray+=`echo $python_libraries_elem ' ' `
   fi
   export newarray
done


for elem in $newarray; do
   echo $elem >> $requerimentsFile

done


echo -e "\nRUN pip3 install -r requirements.txt" >> $dockerfile

echo "new Dockerfile generated!"
echo -e "new requeriments file generated!\n"

#echo "All used libraries were collected"
echo -e "Done!"
