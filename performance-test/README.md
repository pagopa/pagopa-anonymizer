# K6 tests

This is a set of [k6](https://k6.io) tests.

To invoke k6 tests use `run_performance_test.sh` script.


## How to run 🚀

Use this command to launch the tests:

``` shell
sh run_performance_test.sh <local|dev|uat> <load|stress|spike|...> <script-filename> <DB-name> <subkey> <generate-zipped> <template-file-name>
```