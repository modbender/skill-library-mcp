package main

import "fmt"

func add(x int, y int) int {
	return x + y
}

func main() {
	result := add(3, 5)
	fmt.Println("Result:", result)
}
