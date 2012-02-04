# semigroup

A **semigroup** is a pair $(S, \ast)$ where $S$ is a set and $\ast: S \times S \to S$ is an associative binary operation which is a [total function][total_func] (i.e., the binary operation is *closed over $S$*). In other words:

$$ \forall a, b \in S \ a \ast (b \ast c) = (a \ast b) \ast c $$

This is where algebraic structure begins. (Well, kinda. I found on wikipedia there's a thing called a magma, which is a semigroup with the associativity condition relaxed. Not sure if it's studied or what it's used for.)


[total_func]: http://en.wikipedia.org/wiki/Total_function
