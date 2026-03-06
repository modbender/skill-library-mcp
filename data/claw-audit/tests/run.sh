#!/bin/bash
# Test runner - filters TAP output to show only results
# Suppresses all intermediate output from Node.js

exec 2>/dev/null

node --test tests/*.test.mjs 2>/dev/null | \
  tr -d '\t\r' | \
  awk '
    /^ok [0-9]/ {
      sub(/^ok [0-9]* - /, "")
      print "✔", $0
      fflush()
      next
    }
    /^not ok [0-9]/ {
      sub(/^not ok [0-9]* - /, "")
      print "✖", $0
      fflush()
      next
    }
    /^# tests / { tests = $3 }
    /^# pass / { pass = $3 }
    /^# fail / { fail = $3 }
    /^# skip / { skip = $3 }
    END {
      if (tests) {
        print ""
        print "ℹ tests", tests
        print "ℹ pass", pass
        print "ℹ fail", fail
        print "ℹ skipped", skip
      }
    }
  '

exit ${PIPESTATUS[0]}
