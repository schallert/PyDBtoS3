# PyDBtoS3
### A simple yet effective Python script for mysqldump'ing to Amazon S3

PyDBtoS3 is a script that lets you choose databases you would like to backup, and backs them up to Amazon S3.

In `config.json`, you define various settings, including the list of databases that you wish to dump. See `config.sample.json` for the structure of the file, and fill in accordingly.

I made a few personal design decisions (such as making the `tar` creation function an iterable generator) which you can feel free to change as you need.

The `tar` file you create will contain two files, one with the database schema, and one with the actual data from your tables.

When you upload the `tar` file to S3, it will be prefixed with the name of the current server name you define. So if you called your server `MySiteProduction`, then on S3 it will seem as if your tar file is contained in the such a directory, i.e. `MySiteProduction/database_date.tar.gz`.