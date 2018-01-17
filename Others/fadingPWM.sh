#!bin/bash
for a in {1..5}
do
	for b in {0..1023}
	do
		gpio -g pwm 18 $b
	done
	for (( c=1023; c>=0; c-- ))
	do
		gpio -g pwm 18 $c
	done
done
