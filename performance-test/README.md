# K6 tests

This is a set of [k6](https://k6.io) tests.

To invoke k6 tests use `run_performance_test.sh` script.


## How to run 🚀

Use this command to launch the tests:

``` shell
sh run_performance_test.sh <local|dev|uat> <load|stress|spike|...> <script-filename> <DB-name> <subkey> <generate-zipped> <template-file-name>
```

## Distinct-input memory benchmark

From the repository root, with the project requirements installed:

```shell
python performance-test/memory_benchmark.py --requests 30000 --interval 5000
```

This exercises the real Presidio hot path in a single process with ten distinct
synthetic reference tokens per request. It prints JSON snapshots of elapsed time,
current RSS, peak RSS, live lexemes and retained strings. It requires `ps`
(Linux/macOS). Live lexemes are counted by iteration because the spaCy length
counter can include already-freed transient entries.

After warm-up, live lexemes and retained strings should remain constant, rather
than increasing with request count. RSS may fluctuate due to the allocator and OS
memory compression; peak RSS includes model loading. This is not a measurement of
Linux container memory, HTTP throughput, or the capacity of the production cluster.

## HTTP memory soak at 30,000 requests/minute

The existing load script repeats identical text. Use the distinct-input script to
exercise vocabulary retention at **500 requests/second total**, not per pod:

```shell
cd performance-test/src
k6 run \
  -e VARS=env/local.environment.json \
  -e TEST_TYPE=./test-types/soak.json \
  -e SUBSCRIPTION_KEY='<sub-key>' \
  memory_soak.js
```

The test runs for 30 minutes, varies ten reference tokens per request, checks
person masking, and fails on dropped iterations, excessive errors or p99 above
3 seconds.