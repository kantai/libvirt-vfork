#!/bin/bash

expect << EOF

set timeout 25

spawn telnet 192.168.122.1 7000

expect "Trying 192.168.122.1..."
expect "Connected to 192.168.122.1."
expect "Escape character is '^]'."

send "vm_1\r"

expect {
       "forked"   {puts parent}
#       "!"        {}
}

#send "^]\r"

#expect "telnet> "

#send "q\r"

exit

EOF