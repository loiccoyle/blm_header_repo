# BLM headers
BLM headers are no fun to deal with.

Check the [headers](./headers) folder for some generated BLM headers.

# How it works
The headers are generated using [`loiccoyle/blm_header`](https://github.com/loiccoyle/blm_header). Have a look at the [generate_headers.py](./generate_headers.py) file, it should be relatively easy to understand whats going on. The basic gist is the following:

* I get the timings of the changes from `timber`'s BLM metadata (plus a few extra manually added).

* For each timestamp I find the closest fill following it which reaches `STABLE` and start matching on the 2 hours following the `INJPROT` beam mode. This avoids matching on an empty machine which improves the matching quality as it is not matching on noise.
