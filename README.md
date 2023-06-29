# snakemake-float

Snakemake profile for MemVerge Memory Machine Cloud (float).

## Add profile

`git clone https://github.com/edwinyyyu/snakemake-float.git ~/.config/snakemake/snakemake-float/`

## Configuration

In your Snakemake working directory, create file `snakemake-float.yaml` based on the template, specifying arguments to pass to  `float` for job submission. The `extra` option specifies a string to append to the `float` command.

## Examples

### NFS shared working directory

`/etc/exports`

```
SHARED_DIR SUBNET(rw,sync,all_squash,anonuid=UID,anongid=GID)
```

We squash all UIDs and GIDs to those of the owner of SHARED_DIR so that Snakemake has access permissions to all files created by worker instances.

`snakemake-float.yaml`
```yaml
address: "OPCENTER_ADDRESS"
username: "admin"
password: "memverge"
dataVolume: "nfs://NFS_SERVER_ADDRESS/SHARED_DIR:MOUNT_POINT"
extra: "--migratePolicy [enable=true]"
```

`snakemake --profile snakemake-float --jobs VALUE`

### S3FS shared working directory

`s3fs BUCKET_NAME SHARED_DIR -o umask=0000`

We set `umask` so that the user running `snakemake` has access to all files created by worker instances.

`snakemake-float.yaml`
```yaml
address: "OPCENTER_ADDRESS"
username: "admin"
password: "memverge"
dataVolume: "[mode=rw]s3://BUCKET_NAME:MOUNT_POINT"
extra: "--migratePolicy [enable=true]"
```

`snakemake --profile snakemake-float --jobs VALUE`

## Known issues

S3FS: Snakemake will not detect output files by itself. Running `ls` will trigger it to do so for some reason. Maybe run a script that runs `ls` at some interval.