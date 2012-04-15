# PyDBtoS3
### A simple yet effective Python script for mysqldump'ing to Amazon S3

PyDBtoS3 is a script that lets you choose databases you would like to backup, and backs them up to Amazon S3.

In `config.json`, you define various settings, including the list of databases that you wish to dump. See `config.sample.json` for the structure of the file, and fill in accordingly.

I made a few personal design decisions (such as making the `tar` creation function an iterable generator) which you can feel free to change as you need.