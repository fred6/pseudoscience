# group

A **group** is a monoid $(S, \ast, u)$ with an additional property:

$$ \forall a \in S \exists a' \in S \ a \ast a' = a' \ast a = u $$

The element $a'$ is called an *inverse* of $a$, and it turns out that we can prove its uniqueness for each $a \in S$. Suppose $a'$ and $a''$ are two inverses of $a$. Then $a' = a' \ast u = a' \ast (a \ast a'') = (a' \ast a) \ast a'' = u \ast a'' = a''$ by, respectively, 1) the definition of a unit, 2) the definition of an inverse, 3) associativity of $\ast$, 4) the definition of an inverse, 5) definition of a unit. This proves that each $a \in S$ has a *unique* inverse, which you will often see written as $a^{-1}$.

We can now define a new function $\iota: S \to S$ which sends each element to its (provably unique! (and honestly it has to be unique for the function definition to even make sense)) inverse -- that is, $a \mapsto a^{-1}$. Now we have our (perhaps pointlessly) pretty definition: 

A **group** is a quadruple $(S, \ast, u, \iota)$ where $(S, \ast, u)$ is a monoid and for each $a \in S$, $\iota(a) = a^{-1}$, where $a^{-1} \in S$ and $a \ast a^{-1} = a^{-1} \ast a = u$.

