// Count the sum of the array [4, 2, 7, 9, 13, 24], multiply the sum by 3 and display the result.

// declare defines, consts and vars
$multiplier 3                     // $multiplier mentions will become 3
$arraySize 6                      // $arraySize mentions will become 6
$array {4, 2, 7, 0x09, 0x0D, 24}  // will save the array on ROM on $array address
$index [1]                        // a var on RAM of 1 bytes on $index address
$sum [1]                          // a var on RAM of 1 bytes on $sum address
$multiplierIteration [1]          // a var on RAM of 1 bytes on $multiplierIteration address
$result [1]                       // a var on RAM of 1 bytes on $result address

// code
$initializeVars:
    // initialize the variables
    MOV 0 C
    MOV C [$index]
    MOV C [$sum]
    MOV C [$multiplierIteration]
    MOV C [$result]

$sumArray:
    // if $index reached $arraySize then jump to $multiplySum
    MOV [$index] A
    CMP $arraySize
    JAE $multiplySum

    ADD $array     // calculate the address of the next array item
    MOV {A} A     // put the value of the next array item in A
    ADD [$sum]     // add it to the sum
    MOV A [$sum]  // save the result back to $sum

    // increase $index by 1
    MOV [$index] A
    ADD 0x01
    MOV A [$index]
    JMP $sumArray

$multiplySum:
    // if $multiplierIteration reached $multiplier then jump to $displayResult
    MOV [$multiplierIteration] A
    CMP $multiplier
    JAE $displayResult

    // add $sum to $result
    MOV [$result] A
    ADD [$sum]
    MOV A [$result]

    // increase $multiplierIteration by 1
    MOV [$multiplierIteration] A
    ADD 1
    MOV A [$multiplierIteration]
    JMP $multiplySum

$displayResult:
MOV [$result] C
HLT
