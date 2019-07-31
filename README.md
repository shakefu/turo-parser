# Apache Log Parser

This package provides a small utility which will parse apache format logs and
output statistics about the given fields. By default it will count and display
percentages for ip addresses found in the upstream load balancers or the
X-Forwarded-For header.

## Installation

This section provides instructions on installing this tool.

### Binary

Download the provided `turo-parser` binary from the latest Release and place it
in a suitable executable directory. This binary is built against Ubuntu 18.04
on x86_64, but will likely work with most glibc + ELF compatible systems. The
binary is packaged with most of its supporting libraries, so no system
dependencies should be needed.

```bash
$ export RELEASE_URL="https://github.com/shakefu/turo-parser/releases/download/v1.0.0/turo-parser"
$ curl -L $RELEASE_URL > /usr/local/bin/turo-parser
$ chmod +x /usr/local/bin/turo-parser
```

### Docker

A docker container is provided if you want to run the command without having to
install anything to your system, except for Docker of course.

```bash
# Create a docker image from this repository
$ docker build -t shakefu/turo-parser .
```

### Python

The Python package for *turo-parser* can be directly installed as well from
GitHub. This requires you have Python3.6 or later installed on your system.

```
$ pip install git+git://github.com/shakefu/turo-parser.git
```

## Usage

This section describes how to use the *turo-parser* tool.

See the [output.md](./output.md) file for an example of the output generated
when this tool is run.

### Binary or Python install

If you've installed the binary or Python package directly you can invoke
`turo-parser` on the command line.

By default the tool accepts logs on stdin - so you are able to pipe your files
directly into the command. Alternatively, you may supply a filename to read and
parse.

```bash
# Review the command help
$ turo-parser --help
# Parse a log with the tool on stdin
$ cat /var/log/apache/access.log | turo-parser
# Parse a log from a file
$ turo-parser /var/log/apache/access.log
```

### Docker

If you're using the dockerized tool, you'll need to invoke the docker command
and volume mount your logs to be parsed into the container. Pipe to stdin
should work but it complains, and I don't have time to debug it.

```bash
# Parse a log
$ docker run -it -v "/var/log:/var/log" shakefu/turo-parser /var/log/apache/access.log
```

### Options

This section describes the command line options available. Most options can
also be set using environment variables.

#### `--help`

Displays the command line help and exits.

#### `--quiet`, `-q`, `PARSE_QUIET=`

This will minimize the output to only the parsed log statistics.

#### `--format`, `-f` , `PARSE_FORMAT=`

Specifies the parsing format in apache log format.

This defaults to `%v:%p %h[%{X-Forwarded-For}i] %l %u %t "%r" %>s %O "%{Referer}i" "%{User-Agent}i"`.

#### `--fields`, `-l`, `PARSE_FIELDS=`

Specifies the fields to search for values to parse. This allows you to change which fields are used for statistic aggregation.

This defaults to `request_header_x_forwarded_for,remote_host`.

The list of field names is provided by the
[apache-log-parser](https://github.com/rory/apache-log-parser) package. Refer
to the documentation for a full list.

## Design

This section describes the rationale for using various technologies and design
decisions.

- *python* - It's what I've been writing lately, so it was easiest.
- *docker* - Using docker lets me control the build system without having to
  install a toolchain on my development environment or a build host and also
  provide a portable container without worrying about the target platform.
- *[apache-log-parser](https://github.com/rory/apache-log-parser)* - This
  package provides flexible parsing for logs, which allows this tool to be
  useful for more than a single log format. It would've been possible to use
  simple regexes or string parsing to parse a single log, but leveraging this
  library means the tool is reusable in the future, instead of having to write
  another one-off parsing script.
- *[pytool](https://github.com/shakefu/pytool)* - Leveraging this library I
  wrote for the CLI setup and options provides a polished, stable and tested
  framework for the CLI tool, and ensures it works well with the POSIX CLI tool
  style.
- *[pyinstaller](https://github.com/pyinstaller/pyinstaller)* - This is a new
  package I discovered when I looked for ways to bundle full Python packages as
  executables. That it can be statically linked into a single binary means the
  executable itself can be easily distributed, and the final docker image built
  has a minimal attack surface and size.
- *stdin and file support* - Supporting stdin is trivial to add with the
  argparse library and allow this tool to work in a similar fashion to many
  other POSIX style commands.



