#!/bin/bash
JAR_FILE_WITH_DEPENDENCIES=$1
echo "$JAR_FILE_WITH_DEPENDENCIES"

mvn clean package
#
#JAR_FILES=$(find ./target -maxdepth 1 -name "*.jar")
#
#echo "$JAR_FILES"
#
#jar_file=''
#other_jar_file=''
#
#for item in $JAR_FILES
#do
#  if [[ "$item" == *"$JAR_FILE_WITH_DEPENDENCIES"* ]];
#  then
#    echo "It's there."
#    jar_file=$item
#    break
#  else
#      other_jar_file=$item
#  fi
#done
#
#if [[ "$jar_file" != '' ]];
#then
#  echo "run jar file with dependencies"
#  java -jar "$jar_file"
#else
#  echo "run jar file wihout dependencies"
#  java -jar "$other_jar_file"
#fi
