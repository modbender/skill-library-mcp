package main

import "fmt"

func factorial(n int) int {
	if n <= 1 {
		return 1
	}
	return n * factorial(n-1)
}

func sum_range(start int, end int) int {
	total := 0
	for i := start; i < end; i++ {
		total += i
	}
	return total
}

func first_even() int {
	nums := []int{1, 3, 5, 8, 10}
	for _, x := range nums {
		if x%2 == 0 {
			return x
		}
	}
	return -1
}

func assert_demo(x int) {
	if !(x > 0) {
		panic("x must be positive")
	}
	fmt.Println("x is positive:", x)
}

func main() {
	fmt.Println("Factorial 5:", factorial(5))
	fmt.Println("Sum 1..9:", sum_range(1, 10))
	fmt.Println("First even:", first_even())
	assert_demo(42)
}
