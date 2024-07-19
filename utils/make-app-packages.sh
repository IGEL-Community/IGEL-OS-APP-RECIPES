#!/bin/bash
shopt -s extglob
# uncomment set and trap to trace execution
set -x
#trap read debug

# Files that have changed in most recent commit
git diff --name-only HEAD HEAD~1
CHANGEDFILES=`git diff --name-only HEAD HEAD~1`
CHANGEDFILESB=`git diff --name-only HEAD HEAD~1|grep -v ".zip"`

BASEDIR=`pwd`
SRCLOC="$BASEDIR/APP_Source"
ZIPLOCATION="$BASEDIR/APP_Packages"
COMMONREADME="$BASEDIR/utils/readme.txt"
COMMONDISCLAIMER="$BASEDIR/utils/disclaimer.txt"
CATEGORIES="Apps Browsers Multimedia Network Office Scripts Server Tools_Drivers Unified_Communications"

for category in $CATEGORIES; do
    cd $SRCLOC/$category;

    #  look at every folder under the category
    for app in *; do

      echo "in the loop with app = $app"
      if [ -d $app ]; then
        zip_needed=false
        #zip_reason=""
        zip_file="$ZIPLOCATION/$category/$app_community.zip";
        #  Take the zip file string out of changed files so we don't recreate it needlessly
        CHANGEDFILES=${CHANGEDFILES//APP_Packages\/$category\/$app_community.zip/}

        if [ ! -f  $zip_file ]; then
          zip_needed=true;
          #zip_reason="$zip_reason There was no current zip file."
        fi

        #  if the common readme and disclaimer files are in the list of changed files, re-create the zip
        if [[ "$CHANGEDFILES" == *"$COMMONREADME"* ]]; then
            zip_needed=true;
            #zip_reason="$zip_reason COMMONREADME is new."
        fi
        if [[ "$CHANGEDFILES" == *"$COMMONDISCLAIMER"* ]]; then
            zip_needed=true;
            #zip_reason="$zip_reason COMMONDISCLAIMER is new."
        fi


        echo "category/app  = $category/$app"
        #  check the list of changed files in this commit to see if this Custom Partition has changed
        if [[ "$CHANGEDFILES" == *"$category/$app"* ]] ; then
            zip_needed=true;
            #zip_reason="$zip_reason A file in $category/$app has changed."
        fi


        #  create the structure needed, then zip the file to the correct location
        if $zip_needed; then
          echo "Zip needed for app: $app"
          #echo "Because $zip_reason"
          cd $app
          foldername=`grep -i "app=" *.sh`
          foldername=${foldername/*\//}
          foldername=${foldername/\"/}
          echo "Folder name: $foldername"
          echo "Zip file: $zip_file"
          cpt="tmp"
          rm -rf $cpt
          mkdir $cpt
          #mkdir "$cpt/igel"
          mkdir "$cpt/target"
          #cp *.xml "$cpt/igel"
          #cp igel/*.xml "$cpt/igel"
          #cp *.inf "$cpt/target"
          #cp target/*.inf "$cpt/target"
          #cp *.sh "$cpt/target"
          cp *.md "$cpt/target"
          cp -R !(*.xml|*.inf|*.sh|*.md|$cpt) "$cpt/target"
          cp $COMMONREADME "$cpt"
          cp $COMMONDISCLAIMER "$cpt"
          cd $cpt
          zip -r $zip_file .
          cd ..
          rm -rf $cpt
          cd ..
        fi

      fi

    done

    cd ../..

done
