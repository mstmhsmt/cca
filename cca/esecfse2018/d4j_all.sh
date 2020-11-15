#!/bin/bash

CMD='./ddjdemo.py run -a ddmin -o DDX'
#CMD='./ddjdemo.py run -a ddmin --plain -o DDX'
##CMD='./ddjdemo.py run -a ddmin -s -o DDX'

$CMD Chart_d4j
sleep 2
$CMD -p 0 Closure_d4j
sleep 2
$CMD -p 1 Closure_d4j
sleep 2
$CMD -p 2 Closure_d4j
sleep 2
$CMD -p 3 Closure_d4j
sleep 2
$CMD -p 4 Closure_d4j
sleep 2
$CMD -p 5 Closure_d4j
sleep 2
$CMD -p 6 Closure_d4j
sleep 2
$CMD -p 7 Closure_d4j
sleep 2
$CMD -p 0 Lang_d4j
sleep 2
$CMD -p 1 Lang_d4j
sleep 2
$CMD -p 0 Math_d4j
sleep 2
$CMD -p 1 Math_d4j
sleep 2
$CMD -p 2 Math_d4j
sleep 2
$CMD -p 3 Math_d4j
sleep 2
$CMD -p 4 Math_d4j
sleep 2
$CMD -p 5 Math_d4j
sleep 2
$CMD -p 0 Mockito_d4j
sleep 2
$CMD -p 1 Mockito_d4j
sleep 2
$CMD -p 2 Mockito_d4j
sleep 2
$CMD Time_d4j
