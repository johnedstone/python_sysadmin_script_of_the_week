## Files in this directory

```
659659    8 -r-xr-xr-x   1 yourname unixadm      5342 Aug 24 11:45 ./monitor_mail_watch_homework.py
659661    4 -r--r--r--   1 yourname unixadm      2322 Aug 24 12:00 ./README.md
659660    4 -r--r--r--   1 yourname unixadm      2641 Aug 24 11:51 ./monitor_mail_watch_before_argparse.py
659648    8 -r--r--r--   1 yourname unixadm      5537 Aug 24 11:53 ./monitor_mail_watch_ose.py
```

## Notes

- Use the homework script to experiment with yourself on a RHEL 7 server.
- Look at the before_argparse script to see what this script looked like before argparse, and the lack of documentation.
- See the ose script for what is currently being used in the OpenShift env.

```
# Example of runing the homework script
shell> ./monitor_mail_watch_homework.py -d --disable-mail --disregard-file-lock -i 2 -s 0
Iteration: 1
################

/usr/sbin/ntpq -p
stdout:      remote           refid      st t when poll reach   delay   offset  jitter
==============================================================================
+someserver1-old.am. 209.87.233.53    3 u  467  512  377    0.299    1.232   0.228
*someserver2-old.am. 128.252.19.1     2 u  149  512  377    0.311    0.828   0.252
+someserver1.am.booh 198.60.22.240    2 u  477  512  377    0.138   -0.616   0.132
-someserver2.am.booh 199.223.248.99   3 u  372  512  377    0.152   -1.168   0.455
 LOCAL(0)        .LOCL.          10 l  81d   64    0    0.000    0.000   0.000

 stderr:
 return code: 0

 bash -c '[ 1 -eq 2 ]'
 stdout:
 stderr:
 return code: 1

 Iteration: 2
 ################

 /usr/sbin/ntpq -p
 stdout:      remote           refid      st t when poll reach   delay   offset  jitter
 ==============================================================================
 +someserver1-old.am. 209.87.233.53    3 u  467  512  377    0.299    1.232   0.228
 *someserver2-old.am. 128.252.19.1     2 u  149  512  377    0.311    0.828   0.252
 +someserver1.am.booh 198.60.22.240    2 u  477  512  377    0.138   -0.616   0.132
 -someserver2.am.booh 199.223.248.99   3 u  372  512  377    0.152   -1.168   0.455
  LOCAL(0)        .LOCL.          10 l  81d   64    0    0.000    0.000   0.000

  stderr:
  return code: 0

  bash -c '[ 1 -eq 2 ]'
  stdout:
  stderr:
  return code: 1

  defaultdict(<type 'int'>, {"bash -c '[ 1 -eq 2 ]' ": 2})
  dict_values([2])
```
