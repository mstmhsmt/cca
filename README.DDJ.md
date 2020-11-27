# DD/Java: Delta Debugging for Java Programs

DD/Java (DDJ for short) is an experimental implementation of the reported in the following paper.

> Masatomo Hashimoto, Akira Mori, Tomonori Izumida. "Automated Patch Extraction via Syntax- and Semantics-Aware Delta Debugging on Source Code Changes", In Proc. the 26th ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering (ESEC/FSE 2018), 2018, pp. 598-609, DOI:[10.1145/3236024.3236047](https://doi.org/10.1145/3236024.3236047) (paper available also from [here](https://stair.center/archives/research/ddj-esecfse2018)).

DDJ relies on Diff/AST for differencing Java programs.

## Quick start

You can instantly try DDJ by means of [Docker](https://www.docker.com/) and [a ready-made container image](https://hub.docker.com/r/codecontinuum/ddj).

    $ docker pull codecontinuum/ddj

The following command line executes DDJ within a container to find failure inducing changes between `1183g` (good version) and `1183b` (bad version) of `logback_ddj` (target project).  The `--include` options specify the relative paths of the source directories. The results will be placed at `logback_ddj/__CCA__YYYYMMDDHHMMSS/dd/patches/`.

    $ tar Jxf regression_examples/logback_ddj.txz
    $ ./cca.py ddjava --include logback-access/src/main/java --include logback-classic/src/main/java --include logback-core/src/main/java logback_ddj 1183g 1183b

Note that DDJ assumes that scripts for building (`build.sh` by default) and testing (`test.sh` by default) are placed at the good version `logback_ddj/1183g`.
If you want to install some packages or other files required to implement build and/or test scripts, put `install_dependencies.sh` at the target project directory (e.g. `regression_examples/hsqldb_ddj`).

You can also try a language agnostic DD/Plain (DDP for short) that relies on `diff` command for differencing programs. The results will be placed at `logback_ddj/__CCA__YYYYMMDDHHMMSS/dd/delta/`.

    $ ./cca.py ddplain --include logback-access/src/main/java --include logback-classic/src/main/java --include logback-core/src/main/java --lang java logback_ddj 1183g 1183b

Note that `--lang` option filters source files by their extensions. That is, `--lang java` means that the tool scan only `*.java`. You can append `--lang` options to add other source files of interest.

## Building parsers and Diff/AST

### Requirements

* GNU make
* [OCaml](http://ocaml.org/) (>=4.11.1)
* [OPAM](https://opam.ocaml.org/) (for installing the following packages: camlzip, cryptokit, csv, git-unix, menhir, ocamlnet, pxp, ulex, uuidm.)
* [Volt](https://github.com/codinuum/volt)

### Compilation

The following create `ast/analyzing/bin/{parsesrc.opt,diffast.opt}`.

    $ cd src
    $ make

They should be used via shell scripts `ast/analyzing/bin/{parsesrc,diffast}` to set some environment variables.

## Building docker image

The following command line creates a docker image named `cca`.  In the image, the framework is installed at `/opt/cca`.

    $ docker build -t cca .

## License

Apache License, Version 2.0
