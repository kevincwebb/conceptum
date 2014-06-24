#!/bin/sh

dir=$VIRTUAL_ENV

if [ "$dir" = "" ]
then
    echo "Error: please activate your virtual environment"
    exit
fi

dir=$dir/lib/python2.7/site-packages

if [ ! -d $dir/threadedcomments ]
then
    echo "Error: please install threadedcomments using pip"
    exit
fi

cd $dir/threadedcomments

echo "Found \'django_comments\' in these files:"
find . -name "*.py" -type f | xargs grep -l "django\.contrib\.comments"

echo
echo "Replacing..."
find . -name "*.py" -type f | xargs sed -i s/"django\.contrib\.comments"/"django_comments"/g

echo "Done!"
exit
