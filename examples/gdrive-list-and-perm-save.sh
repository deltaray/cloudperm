#!/bin/bash

# By Mark Krenz, 2019-03-07

# Set organization to a name you want to use to identify the output files.
# For example, your project name.
organization="identifierfordoctree"

# Set this to the unique Google Drive Document ID of the folder you want
# to start from and decend into.
startfolderid="f50ab781-dc0b-4e0b-93fe-ee978d857755"

# Path to the cloudperm software.
bindir=$HOME/cloudperm

# Where the output report files will be saved.
outputdir=$HOME

##########################################################
# You shouldn't need to modify anything below this line.

cd "$bindir"

date=$( date +%Y%m%d )


documentlistfile=${outputdir}/google-drive-files-${organization}-${date}.txt

${bindir}/listFiles -r "${startfolderid}" | tee "${documentlistfile}"


permissionlistfile=${outputdir}/google-drive-files-${organization}-${date}-permissions.txt

grep -v -e "Total files:" "${documentlistfile}" | \
 while read docid undef ; do
    echo "Doc Id: ${docid}"
    ${bindir}/permissionList "${docid}"
    echo
 done \
 | tee "${permissionlistfile}"


# The command below is an example of an analysis command you may want to run after this program is done.
#grep -e "Doc Id:" -e "Path:" -e WARNING: "${permissionlistfile}" | grep -B2 WARNING: | less -S +/WARNING
