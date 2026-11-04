# Verified 348,087-vertex Web-Google Graph Burning experiment

This is the largest successful Graph Burning job completed by the team so
far. The input contains 348,087 vertices and 1,128,693 undirected
connections in eight parts. The eight random, eligible but non-optimized
source rounds are:
`96901:113758:455241:73976:310174:473800:320304:118094`.

Python predicted 243,095 burned and 104,992 unburned vertices. Giraph ran on:

```text
/user/mca2025/giraph_learning/web_google_348k_burning_input
```

and wrote:

```text
/user/mca2025/giraph_learning/web_google_348k_burning_output/part-00000
```

The [actual Giraph output](giraph-actual.tsv) contains 348,087 rows and
matches the Python `expected.tsv` exactly (`cmp` exit code `0`). The
`python-preview/` folder contains the eight round-state and burned-edge
tables. The result verifies correctness for this random schedule; it is not
an optimization or minimum-burning-number result.
