#!/bin/bash
kill -9 $(pgrep python | awk '$1>3000')
